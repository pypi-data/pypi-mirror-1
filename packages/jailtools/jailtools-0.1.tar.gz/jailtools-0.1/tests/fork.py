import os
import time

for i in range(0, 5):
    pid = os.fork()
    if pid == 0:
        print "Sleeping in", i
        time.sleep(10)
        os._exit(0)

os.wait()
