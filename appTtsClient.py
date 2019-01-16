import sys
import signal
import threading
import time
import pyttsx3

from wosBattleshipServer.cTtsCommEngineClient import TtsClientCommEngine

# Global variable for memory sharing between threads
is_running = False
msg_list = list()


def signal_handler(sig, frame):
    global is_running
    is_running = False


def tts_ops_thread():
    global is_running
    global msg_list

    # initialize the tts engine
    engine = pyttsx3.init()
    engine.setProperty('rate', 120)
    engine.setProperty('volume', 0.9)

    # Main thread operation
    print("*** tts_ops_thread start ***")
    engine.say("TTS engine started")
    engine.runAndWait()
    while is_running:
        if len(msg_list) > 0:
            msg = msg_list.pop(0)
            engine.say(msg)
            engine.runAndWait()
        else:
            time.sleep(0.5)
    engine.say("TTS engine ended")
    engine.runAndWait()
    print("*** tts_ops_thread exit ***")


def tts_rcv_thread():
    global is_running
    global msg_list

    print("*** tts thread start ***")
    # Communication Engine Thread
    comm_engine = TtsClientCommEngine()
    comm_engine.start()

    next_runtime = time.time() + 1.0
    while is_running:
        msg = comm_engine.recv()
        curr_time = time.time()

        if isinstance(msg, str):
            print("RECV @ %s: %s" % (time.strftime("%H%M%S", time.gmtime(curr_time)), msg))
            # Perform TEXT-TO-SPEECH operation
            if len(msg_list) < 25:
                msg_list.append(msg)
            else:
                print("[Buffer full] DROP %s" % msg)
        # else:
        #     print("RECV @ %s: <NOTHING>" % (time.strftime("%H%M%S", time.gmtime(curr_time))))

        diff = next_runtime - curr_time
        if diff <= -2.0:
            next_runtime = time.time() + 1.0
        elif diff <= 0:
            next_runtime = next_runtime + 1.0
        elif diff > 10:
            next_runtime = time.time() + 1.0
        else:
            time.sleep(diff)
    comm_engine.stop()
    print("*** tts thread exit ***")


if __name__ == '__main__':
    print("** \"%s\" has started [%s]" % (sys.argv[0], time.ctime(time.time())))
    is_running = True
    signal.signal(signal.SIGINT, signal_handler)

    # Text-to-Speech Thread
    thread_tts_ops = threading.Thread(name='tts-ops-thread',
                                      target=tts_ops_thread)
    thread_tts_ops.start()

    # start the server thread
    thread_tts_rcv = threading.Thread(name='tts-rcv-thread',
                                       target=tts_rcv_thread)
    thread_tts_rcv.start()

    thread_tts_rcv.join()
    thread_tts_ops.join()
    print("** \"%s\" has ended [%s]" % (sys.argv[0], time.ctime(time.time())))
