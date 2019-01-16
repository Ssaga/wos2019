import zmq

from cCommonCommEngine import ConnInfo


#
class TtsServerCommEngine:

    def __init__(self, conn_if=ConnInfo("127.0.0.1", 8889)):
        self.conn_if = conn_if
        self.context = None
        self.socket = None
        self.reset_conn = False
        self.is_ready = False

    def start(self):
        # setup the server
        self.setup_server()
        print("\tTTS Server CommEngine Started...")
        self.is_ready = True

    def stop(self):
        self.is_ready = False
        # stop the server
        self.teardown_server()
        print("\tTTS Server CommEngine Stopped...")

    def setup_server(self):
        # create the req-rep i/f with the server
        if self.context is not None:
            print("\tRecreate TTS server...")
            self.teardown_server(self)
        self.context = zmq.Context()
        # self.socket = self.context.socket(zmq.PULL)
        self.socket = self.context.socket(zmq.PUB)
        conn_string = str("tcp://%s:%s" % (self.conn_if.addr, self.conn_if.port,))
        print("\tSetting up TTS server... [%s]" % conn_string)
        self.socket.bind(conn_string)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.set_hwm(5)

    def teardown_server(self):
        # close the connection of the rep socket
        if self.socket is not None:
            try:
                self.poller.unregister(self.socket)
            except:
                print("\t[TTS] Socket is not registered in poller")

            try:
                self.socket.close()
                self.socket = None
            except zmq.ZMQError:
                print("\t[TTS] Error closing the socket")

        # terminate the context
        if self.context is not None:
            try:
                self.context.term()
                self.context = None
            except zmq.ZMQError:
                print("[TTS] Error terminating context")

    def recv(self):
        # do nothing
        print("\t[TTS] Receive operation is not supported");

    def send(self, msg):
        if isinstance(msg, str):
            if self.socket is not None:
                try:
                    print("################## TTS Server: SEND: %s" % msg)
                    self.socket.send_string(msg)
                except zmq.ZMQError:
                    self.reset_conn = True
            else:
                print("\tTTS CommEngine is not started")
        else:
            print("\t[TTS] Input is not string")
