import sys
import time
from copy import deepcopy

from wosBattleshipServer.cCmdCommEngineClient import CmdClientCommEngine

if __name__ == '__main__':
    print("** \"%s\" has started [%s]" % (sys.argv[0], time.ctime(time.time())))
    print("** INPUT: %s" % sys.argv)

    if len(sys.argv) > 1:

        in_data = deepcopy(sys.argv)
        in_data.pop(0)					# Remove the first element
        out_msg = " ".join(in_data)		# Change the list of string to a single line

        clientCommEngine = CmdClientCommEngine()
        clientCommEngine.start()
        clientCommEngine.send(out_msg)
        clientCommEngine.stop()

    else:
        print("No input is provided")

    print("** \"%s\" has ended [%s]" % (sys.argv[0], time.ctime(time.time())))
