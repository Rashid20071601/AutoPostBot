# ========================= Импорт библиотек ========================= #
from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from zoneinfo import ZoneInfo
import logging
import time

from lexicon.lexicon import LEXICON_RU
from keyboards import keyboard_utils
from database.db import add_mailing, update_last_sent, get_mailings
from states.states import MailingState


# ========================= Инициализация логирования и роутера ========================= #
logger = logging.getLogger(__name__)
router = Router()
scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Moscow"))


# ========================= Хендлеры приветствия и помощи ========================= #
async def send_welcome(message: Message):
    logger.info(f"Пользователь {message.from_user.id} нажал на кнопку '/start'...")
    await message.answer(
        text=LEXICON_RU['welcome'],
        reply_markup=keyboard_utils.main_kb(),
        parse_mode="HTML"
    )
    logger.info(f"Бот ответил пользователю {message.from_user.id}")


async def send_help(message: Message):
    logger.info(f"Пользователь {message.from_user.id} нажал на кнопку '/help'")
    await message.answer(
        text=LEXICON_RU['help'],
        parse_mode="HTML"
    )
    logger.info(f"Бот ответил пользователю {message.from_user.id}")


# ========================= Хендлеры создания поста ========================= #
async def create_mailing(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Пользователь {callback.from_user.id} нажал на кнопку 'Создать пост'...")
    await callback.message.edit_text(
        text=LEXICON_RU['get_mailing'],
        reply_markup=keyboard_utils.back_to_menu_kb(),
        parse_mode="HTML"
    )

    await state.set_state(MailingState.text)
    await callback.answer()
    logger.info(f"Пользователь {callback.from_user.id} перешел в режим создания поста!")


async def mailing_text(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} ввел текст поста...")
    await state.update_data(text=message.text)

    await message.answer(
        text=LEXICON_RU['get_interval'],
        reply_markup=keyboard_utils.back_to_menu_kb(),
        parse_mode="HTML"
    )
    await state.set_state(MailingState.hour)
    logger.info(f"Пользователь {message.from_user.id} ввел час публикации!")


async def mailing_hour(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} ввел час публикации")

    try:
        logger.debug("Преобразование часа в int...")
        hour = int(message.text)

        if hour < 1:
            logger.exception("Час меньше 1!")
            raise ValueError

        await state.update_data(hour=hour)

        await message.answer(
            text=LEXICON_RU['get_interval'],
            reply_markup=keyboard_utils.back_to_menu_kb(),
            parse_mode="HTML"
        )
        await state.set_state(MailingState.minute)
        logger.info(f"Пользователь {message.from_user.id} ввел час публикации!")

    except ValueError:
        logger.exception(f"Пользователь {message.from_user.id} ввел некорректный час!")
        await message.answer(
            text=LEXICON_RU['interval_error'],
            parse_mode="HTML"
        )
        await state.clear()
        await send_welcome(message=message)


async def mailing_minute(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} ввел минуты публикации")

    try:
        logger.debug("Преобразование минут в int...")
        minute = int(message.text)

        if minute < 1:
            logger.exception("Минуты меньше 1!")
            raise ValueError

        await state.update_data(minute=minute)

        await message.answer(
            text=LEXICON_RU['get_channel_id'],
            reply_markup=keyboard_utils.back_to_menu_kb(),
            parse_mode="HTML",
        )
        await state.set_state(MailingState.chanel)
        logger.info(f"Минуты {minute} успешно установлены!")

    except ValueError:
        logger.exception(f"Пользователь {message.from_user.id} ввел некорректные минуты!")
        await message.answer(
            text=LEXICON_RU['interval_error'],
            parse_mode="HTML"
        )
        await state.clear()
        await send_welcome(message=message)


async def mailing_chanel(message: Message, state: FSMContext, bot: Bot):
    logger.info(f"Пользователь {message.from_user.id} ввел ID группы...")

    try:
        logger.debug("Преобразование ID группы в int...")
        chanel_id = int(message.text)

    except ValueError:
        logger.info(f"Пользователь {message.from_user.id} ввел некорректный ID группы!")
        await message.answer(
            text=LEXICON_RU['channel_id_error'],
            parse_mode="HTML"
        )
        await state.clear()
        await send_welcome(message=message)

    try:
        logger.debug("Попытка отправить тестовое сообщение в группу...")
        test_msg = await bot.send_message(chanel_id, LEXICON_RU['test_message'])
        await bot.delete_message(chanel_id, test_msg.message_id)

    except Exception:
        logger.exception("Не удалось отправить тестовое сообщение в группу!")
        await message.answer(
            text=LEXICON_RU['mailing_message_error'],
            parse_mode="HTML",
        )
        await state.clear()
        await send_welcome(message=message)

    logger.info("Тестовое сообщение успешно отправлено!")
    data = await state.get_data()
    await add_mailing(data["text"], data["hour"], data["minute"], chanel_id)
    await message.answer(
        text=LEXICON_RU['mailing_created'],
        parse_mode="HTML"
    )
    await state.clear()
    logger.info("Рассылка успешно создана")


# Публикация поста
async def send_mailing(mailing_id: int, text: str, channel_id: int, bot: Bot) -> None:
    try:
        logger.debug(f"Отправка в канал {channel_id}...")
        await bot.send_message(channel_id, text)
        await update_last_sent(mailing_id, time.time())
    except Exception:
        logger.exception(f"Ошибка отправки в канал {channel_id}")

async def load_mailings(bot: Bot) -> None:
    try:
        mailings = await get_mailings()
        for m in mailings:
            mailing_id, text, hour, minute, channel_id, enabled, last_sent = m
            if enabled:
                scheduler.add_job(
                    send_mailing,
                    trigger="cron",
                    hour=hour,
                    minute=minute,
                    args=[mailing_id, text, channel_id, bot],
                    id=str(mailing_id),
                    replace_existing=True
                )
    except Exception:
        logger.exception(f"Ошибка отправки в канал {channel_id}")


async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Пользователь {callback.from_user.id} нажал на кнопку 'Назад'...")
    await state.clear()

    await callback.message.edit_text(
        text=LEXICON_RU['welcome'],
        reply_markup=keyboard_utils.main_kb(),
        parse_mode="HTML"
    )

    await state.clear()
    await callback.answer()
    logger.info(f"Пользователь {callback.from_user.id} вернулся в главное меню!")




# ========================= Регистрация хэндлеров ========================= #
# /start
router.message.register(send_welcome, Command(commands="start"))

# /help
router.message.register(send_help, Command(commands="help"))

# Запрос текста поста
router.callback_query.register(create_mailing, F.data == "create_post")

# Запрос часов
router.message.register(mailing_text, MailingState.text)

# Запрос минут
router.message.register(mailing_hour, MailingState.hour)

# Запрос ID группы
router.message.register(mailing_minute, MailingState.minute)

# Обработка поста
router.message.register(mailing_chanel, MailingState.chanel)

# Кнопка "Назад"
router.callback_query.register(back_to_menu, F.data == "back_to_menu")