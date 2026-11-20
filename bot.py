import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- НАСТРОЙКИ ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "ВАШ_НОВЫЙ_ТОКЕН")
ADMIN_ID = 8553406744  # Ваш ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- СОСТОЯНИЯ ---
class QuizStates(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()

# --- ГЛАВНОЕ МЕНЮ ---
def get_start_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🚀 Начать тест", callback_data="start_quiz"))
    return builder.as_markup()

# --- КЛАВИАТУРЫ ДЛЯ ВОПРОСОВ ---
def get_q1_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Общаться с людьми", callback_data="q1_1"))
    builder.row(InlineKeyboardButton(text="Работать с цифрами/кодом", callback_data="q1_2"))
    builder.row(InlineKeyboardButton(text="Творить и создавать", callback_data="q1_3"))
    return builder.as_markup()

def get_q2_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Стабильность и график", callback_data="q2_1"))
    builder.row(InlineKeyboardButton(text="Свобода и фриланс", callback_data="q2_2"))
    builder.row(InlineKeyboardButton(text="Свой бизнес", callback_data="q2_3"))
    return builder.as_markup()

def get_q3_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Анализировать данные", callback_data="q3_1"))
    builder.row(InlineKeyboardButton(text="Помогать и обучать", callback_data="q3_2"))
    builder.row(InlineKeyboardButton(text="Придумывать новое", callback_data="q3_3"))
    return builder.as_markup()

# --- ЛОГИКА БОТА ---

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! 👋 Это тест «Какая сфера тебе подходит?».\n"
        "Ответь на 3 вопроса, и я скажу, какая профессия тебе ближе всего.",
        reply_markup=get_start_menu()
    )

@dp.callback_query(F.data == "start_quiz")
async def start_quiz(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(score_a=0, score_b=0, score_c=0)
    await callback.message.edit_text(
        "Вопрос 1: Что тебе нравится делать больше всего?",
        reply_markup=get_q1_menu()
    )
    await state.set_state(QuizStates.q1)
    await callback.answer()

@dp.callback_query(QuizStates.q1)
async def process_q1(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.data == "q1_1": data['score_a'] += 1
    elif callback.data == "q1_2": data['score_b'] += 1
    elif callback.data == "q1_3": data['score_c'] += 1
    await state.update_data(data)
    
    await callback.message.edit_text(
        "Вопрос 2: Что для тебя важнее в работе?",
        reply_markup=get_q2_menu()
    )
    await state.set_state(QuizStates.q2)
    await callback.answer()

@dp.callback_query(QuizStates.q2)
async def process_q2(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.data == "q2_1": data['score_a'] += 1
    elif callback.data == "q2_2": data['score_b'] += 1
    elif callback.data == "q2_3": data['score_c'] += 1
    await state.update_data(data)
    
    await callback.message.edit_text(
        "Вопрос 3: Чем бы ты хотел заниматься в идеале?",
        reply_markup=get_q3_menu()
    )
    await state.set_state(QuizStates.q3)
    await callback.answer()

@dp.callback_query(QuizStates.q3)
async def process_q3(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.data == "q3_1": data['score_a'] += 1
    elif callback.data == "q3_2": data['score_b'] += 1
    elif callback.data == "q3_3": data['score_c'] += 1
    await state.update_data(data)
    
    # Подсчет результатов
    a, b, c = data['score_a'], data['score_b'], data['score_c']
    result_text = ""
    result_name = ""
    
    if a >= b and a >= c:
        result_name = "Менеджер / Коммуникатор"
        result_text = "Ты отлично ладишь с людьми! Тебе подойдет работа в продажах, HR, менеджменте или клиентском сервисе. Ты умеешь слушать и находить общий язык."
    elif b >= a and b >= c:
        result_name = "Аналитик / IT-специалист"
        result_text = "Ты любишь точность и порядок. Тебе подойдет работа с данными, программирование, аналитика или финансовый учет. Ты внимателен к деталям."
    else:
        result_name = "Креатор / Дизайнер"
        result_text = "Ты творческая личность! Тебе подойдет дизайн, маркетинг, контент-мейкинг или любая работа, где нужно придумывать новое."

    # Отправляем результат пользователю
    await callback.message.edit_text(
        f"🎉 Твой результат: *{result_name}*\n\n{result_text}",
        parse_mode="Markdown"
    )
    
    # Отправляем уведомление админу (лид)
    user_info = f"@{callback.from_user.username}" if callback.from_user.username else f"ID: {callback.from_user.id}"
    await bot.send_message(
        ADMIN_ID,
        f"📊 *Новый пройденный тест!*\n"
        f"👤 Пользователь: {user_info}\n"
        f"🎯 Результат: {result_name}\n"
        f"📈 Баллы (A/B/C): {a}/{b}/{c}"
    )
    
    await state.clear()
    await callback.answer()

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
async def handle(request):
    return web.Response(text="Quiz Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server started on port {port}")

async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())