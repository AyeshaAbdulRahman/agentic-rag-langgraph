import sys
import time

with open('test_chat_debug.log', 'w') as f:
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
    
    f.write(f'[{time.time()}] Calling chat()\n')
    f.flush()
    response = ch.chat("What is dementia?")
    f.write(f'[{time.time()}] Chat completed!\n')
    f.write(f'Reply: {response.get("reply", "NO REPLY")[:100]}\n')
    f.flush()

print("Done!")
with open('test_chat_debug.log', 'r') as f:
    print(f.read())
