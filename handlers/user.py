# ========================= Импорт библиотек ========================= #
from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from lexicon.lexicon_ru import LEXICON_RU
from keyboards import keyboard_utils
from states.states import PostState


# ========================= Инициализация логирования и роутера ========================= #
logger = logging.getLogger(__name__)
router = Router()


# ========================= Хендлеры приветствия и помощи ========================= #
# /start
@router.message(Command(commands="start"))
async def send_welcome(message: Message):
    logger.info(f"Пользователь {message.from_user.id} нажал на кнопку '/start'...")
    await message.answer(
        text=LEXICON_RU['welcome'],
        reply_markup=keyboard_utils.admin_main_kb(),
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
async def handle_create_mailing(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Пользователь {callback.from_user.id} нажал на кнопку 'Создать пост'...")
    await callback.message.edit_text(
        text=LEXICON_RU['get_post'],
        reply_markup=keyboard_utils.back_to_menu_kb(),
        parse_mode="HTML"
    )

    await state.set_state(PostState.text)
    await callback.answer()
    logger.info(f"Пользователь {callback.from_user.id} перешел в режим создания поста!")


# Запрос интервала
@router.message(PostState.text)
async def handle_mailing_text(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} ввел текст поста...")
    await state.update_data(text=message.text)

    await message.answer(
        text=LEXICON_RU['get_interval'],
        reply_markup=keyboard_utils.back_to_menu_kb(),
        parse_mode="HTML"
    )
    await state.set_state(PostState.interval)
    logger.info(f"Пользователь {message.from_user.id} ввел интервал!")


# Запрос ID группы
@router.message(PostState.interval)
async def handle_mailing_interval(message: Message, state: FSMContext):
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
        await state.set_state(PostState.chanel)
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
@router.message(PostState.chanel)
async def handle_mailing_chanel(message: Message, state: FSMContext, bot: Bot):
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
            text=LEXICON_RU['post_message_error'],
            parse_mode="HTML",
        )
        await state.clear()
        await send_welcome(message=message)

    await message.answer(
        text=LEXICON_RU['post_created'],
        parse_mode="HTML"
    )
    await state.clear()
    logger.info("Рассылка успешно создана")


# ========================= Хендлеры кнопки "Назад" ========================= #
@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Пользователь {callback.from_user.id} нажал на кнопку 'Назад'...")
    await state.clear()

    await callback.message.edit_text(
        text=LEXICON_RU['welcome'],
        reply_markup=keyboard_utils.admin_main_kb(),
        parse_mode="HTML"
    )

    await state.clear()
    await callback.answer()
    logger.info(f"Пользователь {callback.from_user.id} вернулся в главное меню!")
