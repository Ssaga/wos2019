import time
import json
import numpy as np
import threading
import logging
import sys
import select
import collections

import cMessages
from cServerCommEngine import ServerCommEngine
from wosBattleshipServer.cCmdCommEngineSvr import CmdServerCommEngine

from cCommonGame import Position
from cCommonGame import Size
from cCommonGame import GameState
from cCommonGame import GameStatus
from cCommonGame import GameConfig
from cCommonGame import ShipInfo as ShipInfoDat
from cCommonGame import ShipMovementInfo
from cCommonGame import FireInfo
from cCommonGame import SatcomInfo
from cCommonGame import Action

from wosBattleshipServer.funcIslandGeneration import island_generation
from wosBattleshipServer.funcCloudGeneration import cloud_generation
from wosBattleshipServer.funcCivilianShipsGeneration import civilian_ship_generation
from wosBattleshipServer.funcCivilianShipsMovement import civilian_ship_movement

from wosBattleshipServer.cCommon import ShipInfo
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

		num_move_act = self.game_setting.num_move_act
		num_fire_act = self.game_setting.num_fire_act
		num_satcom_act = self.game_setting.num_satcom_act
		if self.game_setting.en_satillite == False:
			num_satcom_act = 0
		self.game_status = GameTurnStatus(GameState.INIT, num_move_act, num_fire_act, num_satcom_act)

		# Players data
		self.player_status_list = dict()
		self.player_curr_fire_cmd_list = dict()
		self.player_prev_fire_cmd_list = dict()
		self.player_mask_layer = dict()
		self.player_boundary = dict()

		self.turn_map_mask = []

		# Game Setup --------------------------------------------------------------
		# Generate the array required
		self.island_layer = np.zeros((self.game_setting.map_size.y, self.game_setting.map_size.x))
		self.cloud_layer = np.zeros((self.game_setting.map_size.y, self.game_setting.map_size.x))
		self.civilian_ship_list = []
		self.civilian_ship_layer = np.zeros((self.game_setting.map_size.y, self.game_setting.map_size.x))

		# Generate Player mask
		self.generate_player_mask(self.player_mask_layer, self.player_boundary)
		# self.player_mask_layer = self.generate_player_mask()
		print("Player mask: ---------------------------------------------")
		for mask_key in self.player_mask_layer.keys():
			print("Player mask: %s" % mask_key)
			print(self.player_mask_layer[mask_key])

		# Generate the island on the map
		# TODO: Generate the island
		island_generation(self.island_layer, self.game_setting.island_coverage)
		print("Island data: ---------------------------------------------")
		print(self.island_layer)

		# TODO: Generate the cloud
		cloud_generation(self.cloud_layer, self.game_setting.cloud_coverage)
		print("Cloud data: ---------------------------------------------")
		print(self.cloud_layer)

		# TODO: Generate the civilian
		civilian_ship_generation(self.civilian_ship_list, self.game_setting.civilian_ship_count)
		print("Civilian data: ---------------------------------------------")
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
				state_changed = False
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
		# print("********** %s %s" % (len(self.player_status_list), self.game_setting.num_of_player))
		if len(self.player_status_list) >= self.game_setting.num_of_player:
			self.game_status.game_state = GameState.PLAY_INPUT
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
		print("********** Remaining action %s %s %s %s " % (remaining_action, remaining_turn_action.remain_move, remaining_turn_action.remain_fire, remaining_turn_action.remain_satcom))
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
		bc_game_status = GameStatus(self.game_status.game_state, self.game_status.game_round, self.game_status.player_turn)
		self.comm_engine.set_game_status(bc_game_status)


	def state_setup_play_input(self):
		self.game_status.player_turn = (self.game_status.player_turn % self.game_setting.num_of_player) + 1
		self.game_status.reset_turn_remaining_action()

		# initial the mask required for this turn
		self.turn_map_mask = self.player_mask_layer[self.game_status.player_turn]

		# check if this is a beginning of a new round; if so, update the civilian ship and cloud
		if self.game_status.player_turn == 1:
			# Update the game round count
			self.game_status.game_round = self.game_status.game_round + 1

			# generate the cloud to be used for this round
			cloud_generation(self.cloud_layer, self.game_setting.cloud_coverage)

			# generate new position of the civilian ships
			civilian_ship_movement(self.civilian_ship_list, self.game_setting.civilian_ship_move_probility)

			# update the layer for the civilian ship
			self.civilian_ship_layer.fill(0)
			for civilian_ship in self.civilian_ship_list:
				if isinstance(civilian_ship, ShipInfo) and (not civilian_ship.is_sunken):
					for pos in self.civilian_ship.area:
						self.civilian_ship_layer[pos[1],pos[0]] = 1
		# else no update is required
		bc_game_status = GameStatus(self.game_status.game_state, self.game_status.game_round, self.game_status.player_turn)
		self.comm_engine.set_game_status(bc_game_status)


	def state_setup_play_compute(self):
		# Check if its previous fire hit any ships; if so, update the score and ship status
		player_status = self.player_status_list[self.game_status.player_turn]
		fire_cmds = self.player_prev_fire_cmd_list[self.game_status.player_turn]
		if isinstance(fire_cmds, collections.Iterable):
			for fire_cmd in fire_cmds:
				self.state_setup_play_compute_fire(fire_cmd, player_status)
		else:
			self.state_setup_play_compute_fire(fire_cmds, player_status)
		bc_game_status = GameStatus(self.game_status.game_state, self.game_status.game_round, self.game_status.player_turn)
		self.comm_engine.set_game_status(bc_game_status)


	def state_setup_play_compute_fire(self, fire_cmd, player_status):
		if isinstance(fire_cmd, FireInfo):
			fire_pos = [fire_cmd.pos.x, fire_cmd.pos.y]
			player_radar_cross_table_index = self.game_status.player_turn - 1
			for other_player_id, other_player_info in self.player_status_list.items():
				if other_player_id is not self.game_status.player_turn:
					for other_player_ship_info in other_player_info.ship_list:
						if (not other_player_ship_info.is_sunken) and (fire_pos in other_player_ship_info.area):
							# Compute if the ship has been hit
							if self.compute_if_ship_sunk(self.game_setting.radar_cross_table[player_radar_cross_table_index]):
							other_player_ship_info.is_sunken = True
								player_status.hit_enemy_count += 1
								print("HIT SUCC: Player did hit %s:%s [%s] @ [%s, %s]" % (
								other_player_id, other_player_ship_info.ship_id, other_player_ship_info.area, fire_cmd.pos.x, fire_cmd.pos.y))
						else:
								print("HIT FAIL: Player is unable to sink the ship %s:%s [%s] @ [%s, %s]" % (
									other_player_id, other_player_ship_info.ship_id, other_player_ship_info.area,
									fire_cmd.pos.x, fire_cmd.pos.y))
						# Else the other player ship is not within the fire area
						else:
							print("MISSED  : Player did not hit %s:%s [%s] @ [%s, %s]" % (
								other_player_id, other_player_ship_info.ship_id, other_player_ship_info.area, fire_cmd.pos.x, fire_cmd.pos.y))
					# end of for..loop player_ship_list
				# end of Check to skip self
			# end of for..loop player_status_list

			# Check if the player hit any civilian ship
			for civilian_ship_info in self.civilian_ship_list:
				if (not civilian_ship_info.is_sunken) and (fire_pos in civilian_ship_info.area):
					# Compute if the ship has been hit
					if self.compute_if_ship_sunk(self.game_setting.radar_cross_table[player_radar_cross_table_index]):
						civilian_ship_info.is_sunken = True
						player_status.hit_civilian_count += 1
						print("HIT SUCC: Player did hit civilian:%s [%s] @ [%s, %s]" % (
							civilian_ship_info.ship_id, civilian_ship_info.area, fire_cmd.pos.x,
							fire_cmd.pos.y))
					else:
						print("HIT FAIL: Player didn'ti sink the civilian:%s [%s] @ [%s, %s]" % (
							civilian_ship_info.ship_id, civilian_ship_info.area,
							fire_cmd.pos.x, fire_cmd.pos.y))
				# Else the civilian is not within the fire area
		# Else Do nothing
		bc_game_status = GameStatus(self.game_status.game_state, self.game_status.game_round, self.game_status.player_turn)
		self.comm_engine.set_game_status(bc_game_status)

	def compute_if_ship_sunk(self, hit_possibility):
		is_sunk = False
		if np.random.rand() < hit_possibility:
			is_sunk = True
		return is_sunk


	def state_setup_stop(self):
		bc_game_status = GameStatus(self.game_status.game_state, self.game_status.game_round, self.game_status.player_turn)
		self.comm_engine.set_game_status(bc_game_status)
		# Display the score of the game
		print("** Game end ------------------------------------")
		for key, player in self.player_status_list:
			sunken_count = 0
			for ship_info in player.ship_list:
				if ship_info.is_sunken:
					sunken_count += 1
			score = (player.hit_enemy_count * 1.0) - (player.hit_civilian_count * 0.0) - (sunken_count * 0.5)
			print("** \tPlayer %s : score:%s | hit:%s - %s | sunken:%s" %
				  (key, score, player.hit_enemy_count, player.hit_civilian_count, sunken_count))
		print("** ---------------------------------------------")

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
				map_data = np.array([])
				ack = False
				if msg_data.player_id not in self.player_status_list:
					map_data = self.island_layer * self.player_mask_layer[msg_data.player_id]
					ack = True
				reply = cMessages.MsgRepAckMap(ack, map_data.tolist())

			# Check if message is MsgReqRegShips
			elif isinstance(msg_data, cMessages.MsgReqRegShips):
				ack = False
				if msg_data.player_id not in self.player_status_list:
					# add the new player to the list
					player_status = PlayerStatus()
					player_status.ship_list.clear()

					# check if the placement of the ships are ok before adding them to the list
					is_ok = self.check_ship_placement(msg_data.player_id, msg_data.ship_list)
					if is_ok:
						for ship_info_dat in msg_data.ship_list:
							if isinstance(ship_info_dat, ShipInfoDat):
								ship_info = ShipInfo(ship_info_dat.ship_id,
													 Position(ship_info_dat.position.x, ship_info_dat.position.y),
													 ship_info_dat.heading,
													 ship_info_dat.size,
													 ship_info_dat.is_sunken)
								player_status.ship_list.append(ship_info)
								print(ship_info)
						self.player_status_list[msg_data.player_id] = player_status
						ack = True
				reply = cMessages.MsgRepAck(ack)

			# Check if message is MsgReqConfig
			elif isinstance(msg_data, cMessages.MsgReqConfig):
				game_config = GameConfig(self.game_setting.num_of_player,
										 self.game_setting.num_of_rounds,
										 self.game_setting.num_fire_act,
										 self.game_setting.num_move_act,
										 self.game_setting.num_satcom_act,
										 self.game_setting.num_of_row,
										 self.game_setting.polling_rate,
										 Size(self.game_setting.map_size.x, self.game_setting.map_size.y),
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
		if (msg_data is not None) and isinstance(msg_data, cMessages.MsgReq):
			# Check if message is MsgReqTurnInfo
			if isinstance(msg_data, cMessages.MsgReqTurnInfo):
				reply = self.state_exec_play_input_turn(msg_data)

			# Check if message is MsgReqTurnMoveAct
			elif isinstance(msg_data, cMessages.MsgReqTurnMoveAct):
				reply = self.state_exec_play_input_move(msg_data)

			# Check if message is MsgReqTurnFireAct
			elif isinstance(msg_data, cMessages.MsgReqTurnFireAct):
				reply = self.state_exec_play_input_fire(msg_data)

			# Check if message is MsgReqTurnSatAct
			elif isinstance(msg_data, cMessages.MsgReqTurnSatAct):
				reply = self.state_exec_play_input_satcom(msg_data)

			# Check if message is MsgReqConfig
			elif isinstance(msg_data, cMessages.MsgReqConfig):
				game_config = GameConfig(self.game_setting.num_of_player,
										 self.game_setting.num_of_rounds,
										 self.game_setting.num_fire_act,
										 self.game_setting.num_move_act,
										 self.game_setting.num_satcom_act,
										 self.game_setting.num_of_row,
										 self.game_setting.polling_rate,
										 Size(self.game_setting.map_size.x, self.game_setting.map_size.y),
										 self.game_setting.en_satillite,
										 self.game_setting.en_submarine)
				reply = cMessages.MsgRepGameConfig(True, game_config)

			# Check if message is MsgReqTurnInfo
			else:
				if msg_data.player_id != self.game_status.player_turn:
					# Current turn is not for the player
					print("Receive message from player %s, but it is not their turn..." % msg_data.player_id)
				else:
					print("Receive wrong message from player %s, for the wrong state..." % msg_data.player_id)
				reply = cMessages.MsgRepAck(False)

		return reply


	def state_exec_play_input_turn(self, msg_data):

		if (msg_data.player_id == self.game_status.player_turn):
			self_ship_list = list()
			enemy_ship_list = list()
			other_ship_list = list()

			for ship_info in self.player_status_list[msg_data.player_id].ship_list:
				if isinstance(ship_info, ShipInfo):
					ship_info_dat = ShipInfoDat(ship_info.ship_id,
												Position(ship_info.position.x, ship_info.position.y),
												ship_info.heading,
												ship_info.size,
												ship_info.is_sunken)
					self_ship_list.append(ship_info_dat)

			# Get the list of civilian ships
			for ship_info in self.civilian_ship_list:
				if isinstance(ship_info, ShipInfo):
					ship_info_dat = ShipInfoDat(ship_info.ship_id,
												Position(ship_info.position.x, ship_info.position.y),
												ship_info.heading,
												ship_info.size,
												ship_info.is_sunken)
					other_ship_list.append(ship_info_dat)

			# TODO: Get the list of enemy ships
			# TODO: Do we need to differ the enemy and civilian ship? if so, how???
			if True:
				enemy_data_list = [value for key, value in self.player_status_list.items() if
							   key is not msg_data.player_id]
				print("****** %s" % enemy_data_list)
				for enemy_data in enemy_data_list:
					print("****** %s" % enemy_data)
					for ship_info in enemy_data.ship_list:
						if isinstance(ship_info, ShipInfo):
							ship_info_dat = ShipInfoDat(ship_info.ship_id,
														Position(ship_info.position.x, ship_info.position.y),
														ship_info.heading,
														ship_info.size,
														ship_info.is_sunken)
							other_ship_list.append(ship_info_dat)
				print("****** %s" % other_ship_list)
			else:
				pass


			bombardment_data = [value for key, value in self.player_curr_fire_cmd_list.items() if
								key is not msg_data.player_id]

			# compute the map data
			map_data = self.generate_map_data()
			map_data = np.maximum(map_data, self.cloud_layer)  # Add the cloud to the map
			map_data = map_data * self.turn_map_mask  # Add the player default mask

			reply = cMessages.MsgRepTurnInfo(True, self_ship_list, enemy_ship_list, other_ship_list, bombardment_data, map_data.tolist())
		else:
			print("Receive message from player %s, but it is not their turn..." % msg_data.player_id)
			reply = cMessages.MsgRepTurnInfo(False, [], [], [])

		return reply


	def state_exec_play_input_move(self, msg_data):
		ack = False
		if (self.game_status.remaining_action.remain_move >= len(msg_data.move)) and \
				(msg_data.player_id == self.game_status.player_turn):
			for action in msg_data.move:
				if isinstance(action, ShipMovementInfo):
					ship = self.player_status_list[msg_data.player_id].ship_list[action.ship_id]
					if isinstance(ship, ShipInfo):
						if action.get_enum_action() == Action.FWD:
							# Check if the selected ship can move forward
							if self.check_forward_action(msg_data.player_id, ship.position, ship.heading, ship.size):
								ship.move_forward()
							else:
								print("!!! Unable to move forward")
						elif action.get_enum_action() == Action.CW:
							# Check if the selected ship can turn clockwise
							if self.check_turn_cw_action(msg_data.player_id, ship.position, ship.heading, ship.size):
								ship.turn_clockwise()
							else:
								print("!!! Unable to turn CW")
						elif action.get_enum_action() == Action.CCW:
							# Check if the selected ship can turn counter-clockwise
							if self.check_turn_ccw_action(msg_data.player_id, ship.position, ship.heading, ship.size):
								ship.turn_counter_clockwise()
							else:
								print("!!! Unable to turn CCW")
			# Update on the number of remaining move operation
			self.game_status.remaining_action.remain_move -= len(msg_data.move)
			ack = True
		else:
			print("Receive message from player %s, but it is not their turn..." % msg_data.player_id)

		reply = cMessages.MsgRepAck(ack)
		return reply

	def state_exec_play_input_fire(self, msg_data):
		ack = False
		if self.game_status.remaining_action.remain_fire >= len(msg_data.fire) and \
				(msg_data.player_id == self.game_status.player_turn):
			# Update the position the player is hitting
			self.player_prev_fire_cmd_list[msg_data.player_id] = self.player_curr_fire_cmd_list.get(msg_data.player_id)
			self.player_curr_fire_cmd_list[msg_data.player_id] = msg_data.fire
			self.game_status.remaining_action.remain_fire -= 1
			ack = True
		else:
			print("Receive message from player %s, but it is not their turn..." % msg_data.player_id)

		reply = cMessages.MsgRepAck(ack)
		return reply


	def state_exec_play_input_satcom(self, msg_data):
		ack = False
		# ship_list = self.player_status_list[msg_data.player_id].ship_list
		# bombardment_data = [value for key, value in self.player_curr_fire_cmd_list.items() if
		# 					key is not msg_data.player_id]
		map_data = []
		if (self.game_status.remaining_action.remain_satcom > 0) and \
				(msg_data.player_id == self.game_status.player_turn):
			# compute the map data
			map_data = self.generate_map_data()

			# TODO: Compute the satcom mask
			satcom_mask = np.ones((self.game_setting.map_size.y, self.game_setting.map_size.x))

			# update the turn_map_mask w satcom data
			self.turn_map_mask = np.maximum(self.turn_map_mask, satcom_mask)

			# update map data with cloud
			cloud_layer = self.cloud_layer
			if msg_data.satcom.is_sar:
				cloud_layer = np.maximum(cloud_layer, satcom_mask)
			map_data = np.maximum(map_data, cloud_layer)  # Add the cloud to the map

			# update map data with user's mask
			map_mask = self.turn_map_mask
			map_data = map_data * map_mask  # Add the player default mask

			ack = True
		else:
			print("Receive message from player %s, but it is not their turn..." % msg_data.player_id)
			map_data = self.generate_map_data() * self.player_mask_layer[msg_data.player_id]

		# Create the result
		# reply = cMessages.MsgRepTurnInfo(ack, ship_list, bombardment_data, map_data)
		reply = cMessages.MsgRepAckMap(ack, map_data.tolist())
		return reply


	def state_exec_play_compute(self, msg_data):
		# We are not expected to receive any message at this state
		# Hence, we shall reply a negative acknowledgement for any message received
		reply = None
		if msg_data is not None:
			reply = cMessages.MsgRepAck(False);
		return reply


	def state_exec_stop(self, msg_data):
		# We are not expected to receive any message at this state
		# Hence, we shall reply a negative acknowledgement for any message received
		reply = None
		if msg_data is not None:
			reply = cMessages.MsgRepAck(False)
		return reply


	# ---------------------------------------------------------------------------
	def generate_map_data(self):
		map_data = np.zeros((self.game_setting.map_size.y, self.game_setting.map_size.x))
		map_data = np.maximum(map_data, self.island_layer)  # Add the island onto the map
		#map_data = np.maximum(map_data, self.civilian_ship_layer)  # Add the ships onto the map
		return map_data

	#---------------------------------------------------------------------------

	def check_ship_placement(self, player_id, ship_list):
		is_ok = True
		boundary = self.player_boundary[player_id]
		if isinstance(ship_list, collections.Iterable):
			for ship_info_dat in ship_list:
				if isinstance(ship_info_dat, ShipInfoDat):
					# if area is within boundary
					for pos in ship_info_dat.area:
						if (pos[0] < boundary[0][0]) or \
								(pos[0] > boundary[0][1]) or \
								(pos[1] < boundary[1][0]) or \
								(pos[1] > boundary[1][1]):
							print("!!! SHIP [NEW]: %s [%s]" % (ship_info_dat , player_id))
							is_ok = False
				else:
					print("!!! SHIP [NEW]: Incorrect type [not ShipInfoDat] [%s]" % player_id)
					is_ok = False
		else:
			print("!!! SHIP [NEW]: Incorrect type [not Iterable] [%s]" % player_id)
			is_ok = False
		return is_ok

	def check_forward_action(self, player_id, pos, heading, size):
		is_ok = True
		boundary = self.player_boundary[player_id]
		test_ship = ShipInfo(0, pos, heading, size)
		test_ship.move_forward()
		# if area is within boundary
		for pos in test_ship.area:
			if (pos[0] < boundary[0][0]) or \
					(pos[0] > boundary[0][1]) or \
					(pos[1] < boundary[1][0]) or \
					(pos[1] > boundary[1][1]):
				is_ok = False
				print("!!! SHIP [FWD]: %s" % test_ship)

		return is_ok

	def check_turn_cw_action(self, player_id, pos, heading, size):
		is_ok = True
		boundary = self.player_boundary[player_id]
		test_ship = ShipInfo(0, pos, heading, size)
		test_ship.turn_clockwise()
		# if area is within boundary
		for pos in test_ship.area:
			if (pos[0] < boundary[0][0]) or \
					(pos[0] > boundary[0][1]) or \
					(pos[1] < boundary[1][0]) or \
					(pos[1] > boundary[1][1]):
				is_ok = False
				print("!!! SHIP [CW ]: %s" % test_ship)

		return is_ok

	def check_turn_ccw_action(self, player_id, pos, heading, size):
		is_ok = True
		boundary = self.player_boundary[player_id]
		test_ship = ShipInfo(0, pos, heading, size)
		test_ship.turn_counter_clockwise()
		# if area is within boundary
		for pos in test_ship.area:
			if (pos[0] < boundary[0][0]) or \
					(pos[0] > boundary[0][1]) or \
					(pos[1] < boundary[1][0]) or \
					(pos[1] > boundary[1][1]):
				is_ok = False
				print("!!! SHIP [CCW]: %s" % test_ship)
		return is_ok

	#---------------------------------------------------------------------------

	def load_server_setting(self, filename):
		write_config = False
		game_setting = None
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
	def generate_player_mask(self, player_mask_dict, player_boundary):

		# player_mask_dict = dict()
		# player_mask_list = list()

		if isinstance(player_mask_dict, dict) and isinstance(player_boundary, dict):
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
				player_boundary[i+1] = [[x1, x2], [y1, y2]]
				# player_mask_list.append(mask)
				# print(mask)

		# return player_mask_dict


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
