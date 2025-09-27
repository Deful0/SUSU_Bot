import telebot
import logging
from datetime import datetime, time
import os
from dotenv import load_dotenv
import time as time_module
from datetime import datetime, timedelta


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    # Время отправки опросов (часы, минуты)
    POLL_TIMES = [
        #(7, 55),  # 7:55
        (9, 40),  # 9:40
        (11, 25)  # 11:25
    ]

    # Дни недели
    TARGET_DAYS = [1, 2, 3, 4]  # Вт, Ср, Чт, Пт


    logger.info("Бот запущен и начал мониторинг времени...")
    last_sent_time = None

    while True:
        try:
            current_time = datetime.now()
            if should_send_poll(POLL_TIMES, TARGET_DAYS):
                if (last_sent_time is None or
                        last_sent_time.strftime("%Y-%m-%d %H:%M") != current_time.strftime("%Y-%m-%d %H:%M")):

                    logger.info(f"Время отправки опроса: {current_time}")
                    send_poll_once()
                    last_sent_time = current_time

                    time_module.sleep(61)
                else:
                    time_module.sleep(30)
            else:
                time_module.sleep(30)

        except KeyboardInterrupt:
            logger.info("Бот остановлен пользователем")
            break
        except Exception as e:
            logger.error(f"Неожиданная ошибка в основном цикле: {e}")
            time_module.sleep(60)


def should_send_poll(POLL_TIMES, TARGET_DAYS):
    now = datetime.now()
    current_weekday = now.weekday()
    current_time = now.time()

    if current_weekday not in TARGET_DAYS:
        return False

    for target_hour, target_minute in POLL_TIMES:
        target_time = time(target_hour, target_minute)
        if (current_time.hour == target_time.hour and
                current_time.minute == target_time.minute):
            return True

    return False


def send_poll_once():
    try:
        load_dotenv()

        BOT_TOKEN = os.getenv('BOT_TOKEN')
        CHAT_ID = os.getenv('CHAT_ID')

        if not BOT_TOKEN or not CHAT_ID:
            logger.error("Не указаны BOT_TOKEN или CHAT_ID в .env файле")
            return

        question = name_polly()
        options_1, options_2, options_3 = text_polly()

        result = send_telegram_poll(BOT_TOKEN, CHAT_ID, question, options_1, options_2, options_3)

        if result:
            logger.info("Опросы успешно отправлены")
        else:
            logger.error("Не удалось отправить опросы")

    except Exception as e:
        logger.error(f"Ошибка при отправке опроса: {e}")


def name_polly():
    pair_time = datetime.now() + timedelta(minutes=5)
    pair_time_str = pair_time.strftime("%H:%M")
    question = f"⚠️Занимаем очередь на пару в: {pair_time_str}⚠️"
    return question


def text_polly():
    options_1 = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    options_2 = ["11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]
    options_3 = ["21", "22", "23", "24", "25", "26", "27", "28", "29", "30"]
    return options_1, options_2, options_3


def send_telegram_poll(BOT_TOKEN, CHAT_ID, question, options_1, options_2, options_3, poll_type="regular",
                       is_anonymous=False, allows_multiple_answers=False, correct_option_id=None):
    try:
        bot = telebot.TeleBot(BOT_TOKEN)

        for options in [options_1, options_2, options_3]:
            if len(options) < 2:
                logger.error("Для опроса нужно как минимум 2 варианта ответа")
                return False
            if len(options) > 10:
                logger.error("Максимум 10 вариантов ответа")
                options = options[:10]

        bot.send_message(CHAT_ID, "Документация к Боту: https://github.com/Deful0/SUSU_EM_BOT")
        for i, options in enumerate([options_1, options_2, options_3], 1):
            poll_params = {
                'chat_id': CHAT_ID,
                'question': f"{question} (Опрос {i})",
                'options': options,
                'is_anonymous': is_anonymous,
                'allows_multiple_answers': allows_multiple_answers
            }

            sent_poll = bot.send_poll(**poll_params)
            logger.info(f"Опрос {i} успешно отправлен в чат {CHAT_ID}")
            logger.info(f"ID опроса: {sent_poll.poll.id}")

            time_module.sleep(1)

        return True

    except Exception as e:
        logger.error(f"Ошибка при отправке опроса: {e}")
        return False


if __name__ == '__main__':
    main()
