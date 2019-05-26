import time
import sys
import signal
import threading

from wosBattleshipServer.cTtsCommEngineSvr import TtsServerCommEngine
from wosBattleshipServer.cTtsCommEngineMsg import TtsMsg1

import appTtsClient


if __name__ == '__main__':
    print("** \"%s\" has started [%s]" % (sys.argv[0], time.ctime(time.time())))

    tts_comm_engine = TtsServerCommEngine()
    tts_comm_engine.start()

    # initial the parameters
    appTtsClient.is_running = True
    signal.signal(signal.SIGINT, appTtsClient.signal_handler)

    # Text-to-Speech Thread
    thread_tts_ops = threading.Thread(name='tts-ops-thread',
                                      target=appTtsClient.tts_ops_thread)
    thread_tts_ops.start()

    # start the server thread
    thread_tts_rcv = threading.Thread(name='tts-rcv-thread',
                                      target=appTtsClient.tts_rcv_thread)
    thread_tts_rcv.start()

    # wait for 15 seconds
    time.sleep(5)

    # Send String
    msg = "Testing 1 2 3"
    tts_comm_engine.send(msg)

    # Send TtsMsg1
    for i in range(1, 6):
        msg = TtsMsg1(i, str("From Player %s Testing 1 2 3" % i))
        tts_comm_engine.send(msg)

    # Stop the engine
    thread_tts_rcv.join()
    thread_tts_ops.join()
    tts_comm_engine.stop()
    print("** \"%s\" has ended [%s]" % (sys.argv[0], time.ctime(time.time())))
