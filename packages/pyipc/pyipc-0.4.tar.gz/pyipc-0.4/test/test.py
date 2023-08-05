#!/usr/bin/env python
import ipc

__revision__ = "$Id: test.py 6 2005-08-08 21:52:29Z root $"

# Create IPC objects
s = ipc.Semaphore(1)
m = ipc.MessageQueue()
b = ipc.SharedBuffer(16)

def child():
    # 2. Get message
    msg = m.get()[1]
    # 3. Write message length and text into buffer
    b[0] = chr(len(msg)) + msg
    # 4. Decrease semaphore (to zero)
    s.P()
    # 6. Print another text
    print "Good bye, World!"

# Create child process
p = ipc.Process(child, ())
# 1. Post message with type = 1
m.post(1, "Hello, World!")
# 5. Wait for zero value
s()
# 6. Print buffer slice with stored text
print b[1 : ord(b[0]) + 1]
# 7. Wait for child process termination
p()
# Print child's output
print p.stdout.read()[:-1]
