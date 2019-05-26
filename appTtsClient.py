import sys
import signal
import threading
import time
import pyttsx3
import json

from wosBattleshipServer.cTtsCommEngineMsg import TtsMsg1
from wosBattleshipServer.cTtsCommEngineClient import TtsClientCommEngine

# Global variable for memory sharing between threads
is_running = False
msg_list = list()

#
filename = "tts_client_config.cfg"

# ----------------------------------------------------------


class TtsClientConfig:
    def __init__(self,
                 player_playback_volume=[0.9, 0.9, 0.9, 0.9]):
        self.player_playback_volume = player_playback_volume

    def __repr__(self):
        return str(vars(self))

# ----------------------------------------------------------


class TtsClientAppJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        result = None
        if isinstance(obj, TtsClientConfig):
            result = {
                "__class__": "tts_client_config",
                "player_playback_volume": obj.player_playback_volume
            }
        else:
            print(type(obj))
            result = super().default(obj)

        return result


class TtsClientAppJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        result = None
        if '__class__' not in obj:
            result = obj
        else:
            class_type = obj['__class__']
            if class_type == 'tts_client_config':
                result = self.parse_tts_client_config(obj)
            else:
                print("Unsupported class type")

        return result

    @staticmethod
    def parse_tts_client_config(obj):
        return TtsClientConfig(
            player_playback_volume=obj['player_playback_volume']
        )


# ----------------------------------------------------------

def signal_handler(sig, frame):
    global is_running
    is_running = False


def tts_ops_thread():
    global is_running
    global msg_list

    # load the configuration
    write_config = False
    tts_client_config = None
    try:
        with open(filename) as infile:
            tts_client_config = json.load(infile, cls=TtsClientAppJsonDecoder)
        if isinstance(tts_client_config, TtsClientConfig) is not True:
            raise ValueError("Incorrect configuration file parameters (%s)" % filename)
    except:
        print("Unable to load TTS client configuration")
        write_config = True

    if write_config:
        try:
            tts_client_config = TtsClientConfig()
            with open(filename, 'w') as outfile:
                json.dump(tts_client_config, outfile, cls=TtsClientAppJsonEncoder, indent=4)
                print("Created satcom scanner setting: %s" % filename)
        except:
            print("Unable to write satcom scanner setting")

    player_playback_volume = tts_client_config.player_playback_volume

    # initialize the tts engine
    engine = pyttsx3.init()
    engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')
    engine.setProperty('rate', 120)
    engine.setProperty('volume', 0.9)

    # Main thread operation
    print("*** tts_ops_thread start ***")
    engine.say("TTS engine started")
    engine.runAndWait()
    while is_running:
        if len(msg_list) > 0:
            msg = msg_list.pop(0)
            if isinstance(msg, TtsMsg1):
                # set volume to match player
                if msg.player_id <= len(player_playback_volume):
                    engine.setProperty('volume', player_playback_volume[msg.player_id - 1])
                else:
                    engine.setProperty('volume', 0.1)
                engine.say(msg.msg_str)
            elif isinstance(msg, str):
                # set default volume
                engine.setProperty('volume', 1.0)
                engine.say(msg)
            engine.runAndWait()
        else:
            time.sleep(0.5)

    engine.setProperty('volume', 1.0)
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

        if isinstance(msg, str) or isinstance(msg, TtsMsg1):
            print("RECV @ %s: %s" % (time.strftime("%H%M%S", time.gmtime(curr_time)), msg))
            # Perform TEXT-TO-SPEECH operation
            if len(msg_list) < 30:
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

    # initial the parameters
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
