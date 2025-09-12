# Import libraries
from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import logging

from keyboards import inline
from texts import texts
from config import PostState, BOT_TOKEN
from .start import send_welcome


logger = logging.getLogger(__name__)

# --------------- Инициализация бота и диспетчера --------------- #
bot = Bot(token=BOT_TOKEN)



# Запрос текста поста
async def handle_create_mailing(callback: CallbackQuery, state: FSMContext):
    logger.info("Пользователь {callback.from_user.id} нажал на кнопку 'Создать пост'...")
    await callback.message.edit_text(
        texts.get_post,
        reply_markup=inline.back_to_menu_kb(),
        parse_mode="HTML"
    )

    await state.set_state(PostState.text)
    await callback.answer()
    logger.info("Пользователь {callback.from_user.id} перешел в режим создания поста!")

# Запрос интервала
async def handle_mailing_text(message: Message, state: FSMContext):
    logger.info("Пользователь {message.from_user.id} ввел текст поста...")
    await state.update_data(text=message.text)
    await message.answer(
        texts.get_interval,
        reply_markup=inline.back_to_menu_kb(),
        parse_mode="HTML"
    )
    await state.set_state(PostState.interval)
    logger.info("Пользователь {message.from_user.id} ввел интервал!")

# Запрос ID группы
async def handle_mailing_interval(message: Message, state: FSMContext):
    logger.info("Пользователь {message.from_user.id} ввел интервал")
    try:
        logger.debug("Преобразование интервала в int...")
        interval = int(message.text)
        if interval < 1:
            logger.exception("Интервал меньше 1!")
            raise ValueError
        await state.update_data(interval=interval)
        await message.answer(
            texts.get_chanel_id,
            reply_markup=inline.back_to_menu_kb(),
            parse_mode="HTML",
        )
        await state.set_state(PostState.chanel)
        logger.info("Интервал {interval} успешно установлен!")
    except ValueError:
        logger.exception("Пользователь {message.from_user.id} ввел некорректный интервал!")
        await message.answer(
            texts.get_interval_error,
            parse_mode="HTML"
        )
        await state.clear()
        await send_welcome(message=message)

# Обработка поста
async def handle_mailing_chanel(message: Message, state: FSMContext):
    logger.info("Пользователь {message.from_user.id} ввел ID группы...")
    try:
        logger.debug("Преобразование ID группы в int...")
        chanel_id = int(message.text)
    except ValueError:
        logger.info("Пользователь {message.from_user.id} ввел некорректный ID группы!")
        message.answer(
            texts.get_chanel_id_error,
            parse_mode="HTML"
        )
        await state.clear()
        await send_welcome(message=message)

    try:
        logger.debug("Попытка отправить тестовое сообщение в группу...")
        test_msg = await bot.send_message(chanel_id, texts.test_message)
        await bot.delete_message(chanel_id, test_msg.message_id)
    except Exception:
        logger.exception("Не удалось отправить тестовое сообщение в группу!")
        await message.answer(
            texts.post_message_error,
            parse_mode="HTML",
        )
        await state.clear()
        await send_welcome(message=message)

    await message.answer(
        "✅ <b>Рассылка успешно создана!</b> 🎉\n\n"
        "Вы можете управлять рассылками через меню.",
        parse_mode="HTML"
    )
    await state.clear()