#!/usr/bin/env python
import ipc, os

__revision__ = "$Id: test.py 145 2006-07-13 07:03:24Z const $"

# Create IPC objects
s = ipc.Semaphore(1)
m = ipc.MessageQueue()
b = ipc.SharedBuffer(16)
# Fork process
if os.fork():
    # 1. Post message with type = 1
    m.post(1, "Hello, World!")
    # 5. Wait for zero value
    s()
    # 6. Print buffer slice with stored text
    print b[1 : ord(b[0]) + 1]
else:
    # 2. Get message
    msg = m.get()[1]
    # 3. Write message length and text into buffer
    b[0] = chr(len(msg)) + msg
    # 4. Decrease semaphore (to zero)
    s.P()
