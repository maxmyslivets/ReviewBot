import time

from bot import bot
from logger import logger as log


if __name__ == '__main__':
    log.info("Start")
    while True:
        try:
            bot.polling(none_stop=True)

        except Exception as e:
            log.error(f"Error occurred: {e}")
            time.sleep(5)

            continue

        break
    log.info("Bot stopped")
