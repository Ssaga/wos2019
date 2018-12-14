import zmq
import time

from cCommonCommEngine import ConnInfo

#
#
#
class CmdServerCommEngine:
	#
	# polling_rate : unit in milliseconds
	def __init__(self, conn_if=ConnInfo("127.0.0.1", 8888), polling_rate=1000):
		self.conn_if = conn_if
		self.context = None
		self.socket = None
		self.poller = zmq.Poller()
		self.reset_conn = False
		self.polling_rate = polling_rate

	def start(self):
		# setup the server
		self.setup_server()
		print("\tServer CommEngine Started...")
		self.is_ready = True

	def stop(self):
		self.is_ready = False
		# stop the server
		self.teardown_server()
		print("\tServer CommEngine Stopped...")

	def setup_server(self):
		# create the req-rep i/f with the server
		if (self.context is not None):
			print("\tRecreate server...")
			self.teardown_server(self)
		self.context = zmq.Context()
		# self.socket = self.context.socket(zmq.PULL)
		self.socket = self.context.socket(zmq.REP)
		connString = str("tcp://%s:%s" % (self.conn_if.addr, self.conn_if.port,))
		print("\tSetting up server... [%s]" % connString)
		self.socket.bind(connString)
		self.poller.register(self.socket, zmq.POLLIN)

	def teardown_server(self):
		# close the connection of the rep socket
		if (self.socket is not None):
			try:
				self.poller.unregister(self.socket)
			except:
				print("\tSocket is not registered in poller")

			try:
				self.socket.close()
				self.socket = None
			except zmq.ZMQError:
				print("\tError closing the socket")

		# terminate the context
		if (self.context is not None):
			try:
				self.context.term()
				self.context = None
			except zmq.ZMQError:
				print("Error terminating context")


	def recv(self):
		msg_str = None
		if self.socket is not None:
			try:
				socks = dict(self.poller.poll(self.polling_rate))
				if (self.socket in socks) and (socks[self.socket] == zmq.POLLIN):
					msg_str = self.socket.recv_string()
					print("\tServer: RECV: %s" % msg_str)
					self.socket.send_string("OK")
			except zmq.ZMQError:
				self.reset_conn = True
		else:
			print("\tCommEngine is not started")
		return msg_str


	def send(self, msg):
		# do nothing
		print("\tSend operation is not supported")
