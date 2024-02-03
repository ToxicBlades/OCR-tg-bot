# main.py
import threading
from bot_core import start_bot

if __name__ == '__main__':
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()
