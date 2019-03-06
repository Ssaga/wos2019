import zmq

from cCommonCommEngine import ConnInfo


#
class CmdClientCommEngine:
    #
    def __init__(self, conn_if=ConnInfo("127.0.0.1", 8888)):
        self.conn_if = conn_if
        self.context = None
        self.socket = None
        self.reset_conn = False
        self.is_ready = False

    def start(self):
        # set the flag to create the connection with server
        self.reset_conn = True

        print("\tCmd CommEngine Started...")
        # set the flag to indicate that commEngine is ready
        self.is_ready = True

    def stop(self):
        self.is_ready = False
        # end the connection with server
        self.teardown_connect()
        print("\tCmd CommEngine Stopped...")

    def setup_connect(self):
        # create the req-rep i/f with the server
        if self.context is not None:
            print("\tReset connection with server")
            self.teardown_connect()
        self.context = zmq.Context()
        # self.socket = self.context.socket(zmq.PUSH)
        self.socket = self.context.socket(zmq.REQ)
        connString = str("tcp://%s:%s" % (self.conn_if.addr, self.conn_if.port,))
        print("\tSetup connection to server... [%s]" % connString)
        self.socket.connect(connString)
        # self.socket.RCVTIMEO = 2000  # in milliseconds

    def teardown_connect(self):
        # close the connection of the req socket
        if self.socket is not None:
            try:
                self.socket.close()
                self.socket = None
            except:
                print("\tError closing the socket")

        # terminate the context
        if self.context is not None:
            try:
                self.context.term()
                self.context = None
            except:
                print("\tError terminating context")

    def send(self, msg):
        # reset the connection if required
        if self.reset_conn:
            self.setup_connect()
            self.reset_conn = False

        # Publish the command to the server
        try:
            if isinstance(msg, str):
                print("\tSEND: %s" % msg)
                self.socket.send_string(msg)
                reply = self.socket.recv_string()
                print("\tRECV: %s" % reply)
            else:
                print("\tUnsupported message-type. Only string is supported[%s]" % type(msg))
        except zmq.ZMQError:
            self.reset_conn = True

    def recv(self):
        # do nothing
        print("\tReceive operation is not supported")
