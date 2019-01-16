import zmq

from cCommonCommEngine import ConnInfo


#
class TtsClientCommEngine:
    #
    def __init__(self, conn_if=ConnInfo("127.0.0.1", 8889)):
        self.conn_if = conn_if
        self.context = None
        self.socket = None
        self.poller = zmq.Poller()
        self.is_ready = False

    def start(self):
        # set the flag to create the connection with server
        self.setup_connect()
        print("\tTTS CommEngine Started...")
        # set the flag to indicate that commEngine is ready
        self.is_ready = True

    def stop(self):
        self.is_ready = False
        # end the connection with server
        self.teardown_connect()
        print("\tTTS CommEngine Stopped...")

    def setup_connect(self):
        # create the req-rep i/f with the server
        if self.context is not None:
            print("\tReset connection with server")
            self.teardown_connect()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        conn_string = str("tcp://%s:%s" % (self.conn_if.addr, self.conn_if.port,))
        print("\tSetup connection to TTS server... [%s]" % conn_string)
        self.socket.connect(conn_string)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.setsockopt(zmq.SUBSCRIBE, b"");
        self.poller.register(self.socket, zmq.POLLIN)

    def teardown_connect(self):
        # remove the socket from the poller
        if self.poller is not None:
            try:
                self.poller.unregister(self.socket)
            except:
                print("\t[TTS] Unregistering socket")
        # close the connection of the req socket
        if self.socket is not None:
            try:
                self.socket.close()
                self.socket = None
            except:
                print("\t[TTS] Error closing the socket")
        # terminate the context
        if self.context is not None:
            try:
                self.context.term()
                self.context = None
            except:
                print("\t[TTS] Error terminating context")

    def send(self, msg):
        # do nothing
        print("\t[TTS] Receive operation is not supported")

    def recv(self, polling_rate=1000):
        msg = None
        socks = dict(self.poller.poll(polling_rate))
        if (self.socket in socks) and (socks[self.socket] == zmq.POLLIN):
            msg = self.socket.recv_string()
        return msg
