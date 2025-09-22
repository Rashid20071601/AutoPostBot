# ========================= Импорт библиотек ========================= #
from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
import time

from lexicon.lexicon_ru import LEXICON_RU
from keyboards import keyboard_utils
from database.db import add_mailing, update_last_sent, get_mailings
from states.states import MailingState


# ========================= Инициализация логирования и роутера ========================= #
logger = logging.getLogger(__name__)
router = Router()
scheduler = AsyncIOScheduler()


# ========================= Хендлеры приветствия и помощи ========================= #
# /start
@router.message(Command(commands="start"))
async def send_welcome(message: Message):
    logger.info(f"Пользователь {message.from_user.id} нажал на кнопку '/start'...")
    await message.answer(
        text=LEXICON_RU['welcome'],
        reply_markup=keyboard_utils.main_kb(),
        parse_mode="HTML"
    )
    logger.info(f"Бот ответил пользователю {message.from_user.id}")


# /help
@router.message(Command(commands="help"))
async def send_help(message: Message):
    logger.info(f"Пользователь {message.from_user.id} нажал на кнопку '/help'")
    await message.answer(
        text=LEXICON_RU['help'],
        parse_mode="HTML"
    )
    logger.info(f"Бот ответил пользователю {message.from_user.id}")


# ========================= Хендлеры создания поста ========================= #
# Запрос текста поста
@router.callback_query(F.data == "create_post")
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


# Запрос интервала
@router.message(MailingState.text)
async def mailing_text(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} ввел текст поста...")
    await state.update_data(text=message.text)

    await message.answer(
        text=LEXICON_RU['get_interval'],
        reply_markup=keyboard_utils.back_to_menu_kb(),
        parse_mode="HTML"
    )
    await state.set_state(MailingState.interval)
    logger.info(f"Пользователь {message.from_user.id} ввел интервал!")


# Запрос ID группы
@router.message(MailingState.interval)
async def mailing_interval(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} ввел интервал")

    try:
        logger.debug("Преобразование интервала в int...")
        interval = int(message.text)

        if interval < 1:
            logger.exception("Интервал меньше 1!")
            raise ValueError

        await state.update_data(interval=interval)

        await message.answer(
            text=LEXICON_RU['get_channel_id'],
            reply_markup=keyboard_utils.back_to_menu_kb(),
            parse_mode="HTML",
        )
        await state.set_state(MailingState.chanel)
        logger.info(f"Интервал {interval} успешно установлен!")

    except ValueError:
        logger.exception(f"Пользователь {message.from_user.id} ввел некорректный интервал!")
        await message.answer(
            text=LEXICON_RU['interval_error'],
            parse_mode="HTML"
        )
        await state.clear()
        await send_welcome(message=message)


# Обработка поста
@router.message(MailingState.chanel)
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

    data = await state.get_data()
    await add_mailing(data["text"], data["interval"], chanel_id)
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
            mailing_id, text, interval, channel_id, enabled, last_sent = m
            if enabled:
                scheduler.add_job(
                    send_mailing,
                    "interval",
                    minutes=interval,
                    args=[mailing_id, text, channel_id, bot],
                    id=str(mailing_id),
                    replace_existing=True
                )
    except Exception:
        logger.exception(f"Ошибка отправки в канал {channel_id}")



# ========================= Хендлеры кнопки "Назад" ========================= #
@router.callback_query(F.data == "back_to_menu")
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
