import time
import json
import numpy as np
import threading
import logging
import sys
import select

import cMessages
from cServerCommEngine import ServerCommEngine
from wosBattleshipServer.cCmdCommEngineSvr import CmdServerCommEngine

from cCommonGame import GameState
from cCommonGame import GameConfig
from cCommonGame import ShipInfo
from cCommonGame import ShipMovementInfo
from cCommonGame import FireInfo
from cCommonGame import SatcomInfo
from cCommonGame import Action

from wosBattleshipServer.funcIslandGeneration import island_generation
from wosBattleshipServer.funcCloudGeneration import cloud_generation
from wosBattleshipServer.funcCivilianShipsGeneration import civilian_ship_generation

from wosBattleshipServer.cCommon import PlayerStatus
from wosBattleshipServer.cCommon import PlayerTurnActionCount
from wosBattleshipServer.cCommon import GameTurnStatus
from wosBattleshipServer.cCommon import ServerGameConfig
from wosBattleshipServer.cCommon import SvrCfgJsonDecoder
from wosBattleshipServer.cCommon import SvrCfgJsonEncoder

import cMessages

# Global Variable  ---------------------------------------------------------


# --------------------------------------------------------------------------
class WosBattleshipServer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

		# Thread Setup --------------------------------------------------------------
		# load the game setting
		self.game_setting = self.load_server_setting("game_server.cfg")
		# setup the communication engine
		self.comm_engine = ServerCommEngine(self.game_setting.req_rep_conn,
											self.game_setting.pub_sub_conn,
											self.game_setting.polling_rate,
											self.game_setting.bc_rate)
		self.is_running = False
		self.flag_end_game = False
		self.flag_restart_game =False
		self.game_status = GameTurnStatus()

		# Players data
		self.player_status_list = dict()
		self.player_curr_fire_cmd_list = dict()
		self.player_prev_fire_cmd_list = dict()

		# Game Setup --------------------------------------------------------------
		# Generate the array required
		self.island_layer = np.zeros((self.game_setting.map_size.y, self.game_setting.map_size.x))
		self.cloud_layer = np.zeros((self.game_setting.map_size.y, self.game_setting.map_size.x))
		self.civilian_ship_list = []
		self.civilian_ship_layer = np.zeros((self.game_setting.map_size.y, self.game_setting.map_size.x))

		# Generate Player mask
		self.players_mask_layer = self.generate_player_mask()
		print("Player mask:")
		for mask_key in self.players_mask_layer.keys():
			print("Player mask: %s" % mask_key)
			print(self.players_mask_layer[mask_key])

		# Generate the island on the map
		# TODO: Generate the island
		island_generation(self.island_layer, self.game_setting.island_coverage)
		print("Island data:")
		print(self.island_layer)

		# TODO: Generate the cloud
		cloud_generation(self.cloud_layer, self.game_setting.cloud_coverage)
		print("Cloud data:")
		print(self.cloud_layer)

		# TODO: Generate the civilian
		civilian_ship_generation(self.civilian_ship_list, self.game_setting.civilian_ship_count)
		print("Civilian data:")
		print(self.civilian_ship_list)


	def stop(self):
		self.is_running = False


	def end_game(self):
		self.flag_end_game = True


	def restart_game(self):
		self.flag_restart_game = True


	def clear_user(self):
		if self.game_status.game_state == GameState.INIT:
			self.player_status_list.clear()
			self.player_curr_fire_cmd_list.clear()
			self.player_prev_fire_cmd_list.clear()
		else:
			print("Unable to clear users as the game has started")

	def run(self):
		self.is_running = True

		# start the communication engine
		self.comm_engine.start()

		while self.is_running:
			msg_data = self.comm_engine.recv()

			state_changed = self.state_get_next()
			if state_changed:
				print("State Change to %s" % self.game_status.game_state)
				self.state_setup()
			self.state_exec(msg_data)

		# stop the communication engine
		self.comm_engine.stop()

	#---------------------------------------------------------------------------
	# todo: Write the state machine
	def state_get_next(self):
		state_changed = False
		if self.game_status.game_state == GameState.INIT:
			state_changed = self.state_get_next_init()
		elif self.game_status.game_state == GameState.PLAY_INPUT:
			state_changed = self.state_get_next_play_input()
		elif self.game_status.game_state == GameState.PLAY_COMPUTE:
			state_changed = self.state_get_next_play_compute()
		elif self.game_status.game_state == GameState.STOP:
			state_changed = self.state_get_next_stop()
		else:
			print("Unsupported state")

		# Just reset the "restart flag"
		self.flag_restart_game = False

		return state_changed


	def state_get_next_init(self):
		state_changed = False
		# check if all the player has registered
		if len(self.player_status_list) >= self.game_setting.num_of_player:
			self.game_status.game_state == GameState.PLAY_INPUT
			state_changed = True
		else:
			print("Waiting for %s remaining player registeration" % (
						self.game_setting.num_of_player - len(self.player_status_list)))
		return state_changed


	def state_get_next_play_input(self):
		state_changed = False

		remaining_turn_action = self.game_status.remaining_action
		remaining_action = remaining_turn_action.remain_move + remaining_turn_action.remain_fire + remaining_turn_action.remain_satcom

		# todo: add a condition for player timeout
		if (remaining_action <= 0) or (False):
			self.game_status.game_state = GameState.PLAY_COMPUTE
			state_changed = True

		return state_changed


	def state_get_next_play_compute(self):
		state_changed = True

		# set the default next state to PLAY_INPUT
		self.game_status.game_state = GameState.PLAY_INPUT

		# check if we have reach the end of the game
		if self.game_status.player_turn == self.game_setting.num_of_player:
			if (self.game_status.game_round == self.game_setting.num_of_rounds) \
				or (self.flag_end_game):
				# time to end the game...
				self.game_status.game_state = GameState.STOP

		return state_changed


	def state_get_next_stop(self):
		state_changed = False

		if self.flag_restart_game == True:
			self.game_status.game_state == GameState.INIT
			state_changed = True

		return state_changed

	#---------------------------------------------------------------------------
	def state_setup(self):
		if self.game_status.game_state == GameState.INIT:
			self.state_setup_init()
		elif self.game_status.game_state == GameState.PLAY_INPUT:
			self.state_setup_play_input()
		elif self.game_status.game_state == GameState.PLAY_COMPUTE:
			self.state_setup_play_compute()
		elif self.game_status.game_state == GameState.STOP:
			self.state_setup_stop()
		else:
			print("Unsupport game state")


	def state_setup_init(self):
		self.flag_end_game = False
		self.flag_restart_game = False
		self.game_status.player_turn = 0
		self.game_status.game_round = 0
		self.game_status.clear_turn_remaining_action()


	def state_setup_play_input(self):
		self.game_status.player_turn = (self.game_status.player_turn % self.game_setting.num_of_player) + 1
		self.game_status.game_round = self.game_status.game_round + 1
		self.game_status.reset_turn_remaining_action()

		# initial the mask required for this turn
		self.turn_map_mask = self.players_mask_layer[self.game_status.player_turn]

		if self.game_status.player_turn == 1:
			# generate the cloud to be used for this round
			cloud_generation(self.cloud_layer, self.game_setting.cloud_coverage)

			# generate new position of the civilian ships
			civilian_ship_generation(self.civilian_ship_list)

			# update the layer for the civilian ship
			self.civilian_ship_layer.fill(0)
			for civilian_ship in self.civilian_ship_list:
				for pos in self.civilian_ship.area:
					self.civilian_ship_layer[pos[1],pos[0]] = 1
		# else no update is required


	def state_setup_play_compute(self):
		# Compute the score of current turn
		# TODO: Check if any of the ship has been hit
		#		if so, update the score and ship status
		pass


	def state_setup_stop(self):
		# TODO: Display or Send the score of the game
		pass


	#---------------------------------------------------------------------------
	def state_exec(self, msg_data):
		reply = None
		if self.game_status.game_state == GameState.INIT:
			reply = self.state_exec_init(msg_data)
		elif self.game_status.game_state == GameState.PLAY_INPUT:
			reply = self.state_exec_play_input(msg_data)
		elif self.game_status.game_state == GameState.PLAY_COMPUTE:
			reply = self.state_exec_play_compute(msg_data)
		elif self.game_status.game_state == GameState.STOP:
			reply = self.state_exec_stop(msg_data)
		else:
			print("Unsupport game state")

		if reply is not None:
			print("REPLY: %s" % vars(reply))
			self.comm_engine.send(reply)


	def state_exec_init(self, msg_data):
		# process the reply for any input message
		reply = None
		#
		if msg_data is not None:
			# Check if message is MsgReqRegister
			if isinstance(msg_data, cMessages.MsgReqRegister):
				map_data = []
				ack = False
				if msg_data.player_id not in self.player_status_list:
					map_data = self.island_layer * self.players_mask_layer[msg_data.player_id]
					ack = True
				reply = cMessages.MsgRepAckMap(ack, map_data)

			# Check if message is MsgReqRegShips
			elif isinstance(msg_data, cMessages.MsgReqRegShips):
				ack = False
				if msg_data.player_id not in self.player_status_list:
					# add the new player to the list
					player_status = PlayerStatus()
					player_status.ship_list.extend(msg_data.ship_list)
					self.player_status_list[msg_data.player_id] = player_status
					ack = True
				reply = cMessages.MsgRepAck(ack)

			# Check if message is MsgReqConfig
			elif isinstance(msg_data, cMessages.MsgReqConfig):
				game_config = GameConfig(self.game_setting.num_of_rounds,
										 self.game_setting.en_satillite,
										 self.game_setting.en_submarine)
				reply = cMessages.MsgRepGameConfig(True, game_config)
			else:
				reply = cMessages.MsgRepAck(False)

		return reply


	def state_exec_play_input(self, msg_data):
		# process the reply for any input message
		reply = None
		# process the reply for any input message
		if msg_data is not None:
			# Check if message is MsgReqTurnInfo
			if isinstance(msg_data, cMessages.MsgReqTurnInfo):
				ship_list = self.player_status_list[msg_data.player_id].ship_list
				bombardment_data = [ value for key, value in self.player_curr_fire_cmd_list.items() if key is not msg_data.player_id]

				# compute the map data
				map_data = self.generate_map_data()
				map_data = np.maximum(map_data, self.cloud_layer)				# Add the cloud to the map
				map_data = map_data * self.turn_map_mask						# Add the player default mask

				reply = cMessages.MsgRepTurnInfo(True, ship_list, bombardment_data, map_data)

			# Check if message is MsgReqTurnMoveAct
			elif isinstance(msg_data, cMessages.MsgReqTurnMoveAct):
				ack = False
				if self.game_status.remaining_action.remain_move >= len(msg_data.move):
					for action in msg_data.move:
						if isinstance(action, ShipMovementInfo):
							ship = self.player_status_list[msg_data.msg_data.player_id].ship_list[action.ship_id]
							if action.get_enum_action() == Action.FWD:
								ship.move_forward()
							elif action.get_enum_action() == Action.CW:
								ship.turn_clockwise()
							elif action.get_enum_action() == Action.CCW:
								ship.turn_counter_clockwise()
					# Update on the number of remaining move operation
					self.game_status.remaining_action.remain_move -= len(msg_data.move)
					ack = True
				reply = cMessages.MsgRepAck(ack)

			# Check if message is MsgReqTurnFireAct
			elif isinstance(msg_data, cMessages.MsgReqTurnFireAct):
				ack = False
				if self.game_status.remaining_action.remain_fire >= len(msg_data.fire):
					# Update the position the player is hitting
					self.player_prev_fire_cmd_list[msg_data.player_id] = self.player_curr_fire_cmd_list[msg_data.player_id]
					self.player_curr_fire_cmd_list[msg_data.player_id] = msg_data.fire
					self.game_status.remaining_action.remain_fire -= 1
					ack = True
				reply = cMessages.MsgRepAck(ack)

			# Check if message is MsgReqTurnSatAct
			elif isinstance(msg_data, cMessages.MsgReqTurnSatAct):
				ack = False
				ship_list = self.player_status_list[msg_data.player_id].ship_list
				bombardment_data = [value for key, value in self.player_curr_fire_cmd_list.items() if
									key is not msg_data.player_id]
				map_data = self.generate_map_data() * self.turn_map_mask

				if self.game_status.remaining_action.remain_satcom > 0:
					# compute the map data
					map_data = self.generate_map_data()

					# TODO: get the satcom mask
					satcom_mask = np.ones((self.game_setting.map_size.y, self.game_setting.map_size.x))

					# update the turn_map_mask
					self.turn_map_mask = np.maximum(self.turn_map_mask, satcom_mask)

					# update map data with cloud
					cloud_layer = self.cloud_layer
					if msg_data.satcom.is_sar:
						cloud_layer = np.maximum(cloud_layer, satcom_mask)
					map_data = np.maximum(map_data, cloud_layer)		# Add the cloud to the map

					# update map data with user's mask
					map_mask = self.turn_map_mask
					map_data = map_data * map_mask						# Add the player default mask

					ack = True
				# Create the result
				reply = cMessages.MsgRepTurnInfo(ack, ship_list, bombardment_data, map_data)

			# Check if message is MsgReqConfig
			elif isinstance(msg_data, cMessages.MsgReqConfig):
				game_config = GameConfig(self.game_setting.num_of_rounds,
										 self.game_setting.en_satillite,
										 self.game_setting.en_submarine)
				reply = cMessages.MsgRepGameConfig(True, game_config)

			# Check if message is MsgReqTurnInfo
			else:
				reply = cMessages.MsgRepAck(False)

		return reply


	def state_exec_play_compute(self, msg_data):
		# reply a negative acknowledgement for any message received
		if msg_data is not None:
			# Check if its previous fire hit any ships
			# TODO: ...
			pass


	def state_exec_stop(self, msg_data):
		# reply a negative acknowledgement for any message received
		if msg_data is not None:
			# TODO: ...
			pass


	# ---------------------------------------------------------------------------
	def generate_map_data(self):
		map_data = np.zeros((self.game_setting.map_size.y, self.game_setting.map_size.x))
		map_data = np.maximum(map_data, self.island_layer)  # Add the island onto the map
		map_data = np.maximum(map_data, self.civilian_ship_layer)  # Add the ships onto the map
		return map_data
	#---------------------------------------------------------------------------

	def load_server_setting(self, filename):
		write_config = False
		game_setting = None
		# try:
		#     fp = open(filename, 'r')
		#     game_setting = json.load(fp, cls=SvrCfgJsonDecoder)
		# except:
		#     print("Unable to load server setting")
		#     write_config = True
		#
		# if write_config:
		#     try:
		#         fp = open(filename, 'w')
		#         json.dump(fp, game_setting, cls=SvrCfgJsonEncoder)
		#     except:
		#         print("Unable to write server setting")
		try:
			with open(filename) as infile:
				game_setting = json.load(infile, cls=SvrCfgJsonDecoder)
		except:
			print("Unable to load server setting")
			write_config = True

		if write_config:
			try:
				game_setting = ServerGameConfig()
				with open(filename, 'w') as outfile:
					json.dump(game_setting, outfile, cls=SvrCfgJsonEncoder, indent=4)
			except:
				print("Unable to write server setting")

		return game_setting

	#---------------------------------------------------------------------------
	def generate_player_mask(self):

		player_mask_dict = dict()
		# player_mask_list = list()

		col_count = int(np.ceil(self.game_setting.num_of_player / self.game_setting.num_of_row))
		#row_count = int(self.game_setting.num_of_player / col_count)
		row_count = self.game_setting.num_of_row

		player_x_sz = int(self.game_setting.map_size.x / col_count)
		player_y_sz = int(self.game_setting.map_size.y / row_count)

		for i in range(self.game_setting.num_of_player):
			x1 = int((i % col_count) * player_x_sz)
			x2 = x1 + player_x_sz
			y1 = int((i // col_count) * player_y_sz)
			y2 = y1 + player_y_sz
			# print(i, x1, x2, y1, y2)

			mask = np.zeros((self.game_setting.map_size.y, self.game_setting.map_size.x))
			mask[y1:y2, x1:x2] = 1
			player_mask_dict[i+1] = mask
			# player_mask_list.append(mask)
			# print(mask)

		return player_mask_dict


def main():

	flag_quit_game = False

	print("WOS Battlership Server -- started")
	wosServer = WosBattleshipServer()
	wosServer.start()

	# start the user-input command server
	cmdServer = CmdServerCommEngine()
	cmdServer.start()
	while not cmdServer.is_ready:
		time.sleep(1)
	print("WOS Battlership Server -- Cmd Server Ready")

	# Game Main exec --------------------------------------------------------------
	while flag_quit_game is not True:
		inp = cmdServer.recv()
		if inp is not None:
			inp = inp.strip()
			inp = inp.upper()

			print("RECV CMD: %s" % inp)

			if inp == 'QUIT':
				flag_quit_game = True
			elif inp == 'END':
				wosServer.end_game()
			elif inp == "RESTART":
				wosServer.restart_game()
			elif inp == 'RESET':
				# TODO: RESET THE wosServer
				pass
			elif inp == 'CLEAR':
				wosServer.clear_user()
			else:
				print("Invalid command : %s" % inp)

		# input = select.select([sys.stdin], [], [], 1)[0]
		# if input:
		# 	value = sys.stdin.readline().rstrip()
		# 	if value == 'quit':
		# 		flag_quit_game = True
		# 	elif value == 'end':
		# 		pass
		# 	else:
		# 		print("Invalid command : %s" % value)

	# Server Teardown --------------------------------------------------------------
	# Stop the user-input command server
	cmdServer.stop();

	# Stop the communication engine and wait for it to stop
	wosServer.stop();
	wosServer.join()

	print("WOS Battlership Server -- end")



if __name__ == '__main__':
	print("*** %s (%s)" % (__file__, time.ctime(time.time())))
	main()
