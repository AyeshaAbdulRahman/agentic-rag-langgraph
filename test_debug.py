import sys
import time

with open('test_debug.log', 'w') as f:
    f.write(f'[{time.time()}] Starting test\n')
    f.flush()
    
    f.write(f'[{time.time()}] Importing ChatHandler\n')
    f.flush()
    from chatbot import ChatHandler
    f.write(f'[{time.time()}] ChatHandler imported\n')
    f.flush()
    
    f.write(f'[{time.time()}] Creating instance\n')
    f.flush()
    ch = ChatHandler()
    f.write(f'[{time.time()}] Instance created!\n')
    f.flush()

print("Done!")
with open('test_debug.log', 'r') as f:
    print(f.read())
