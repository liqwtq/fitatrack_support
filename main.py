import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_TELEGRAM_ID = 786717735

# === FSM States ===
class SupportForm(StatesGroup):
    waiting_for_question = State()

# === Bot setup ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# === Handlers ===

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer(
        "👋 Welcome to Support!\n\nPlease describe your issue or question, and we'll get back to you as soon as possible.💬",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(SupportForm.waiting_for_question)

@dp.message(SupportForm.waiting_for_question)
async def receive_question(message: Message, state: FSMContext):
    question = message.text
    user = message.from_user

    msg = (
        f"📨 New support message:\n\n"
        f"👤 From: @{user.username or user.full_name} (ID: {user.id})\n"
        f"📝 Message: {question}"
    )

    try:
        await bot.send_message(chat_id=ADMIN_TELEGRAM_ID, text=msg)
        await message.answer("✅ Your message has been sent! Support will reply soon.")
    except Exception as e:
        await message.answer("⚠️ Failed to send message to support. Please try again later.")

    await state.clear()

@dp.message(F.text.startswith("/contact"))
async def reply_to_user(message: Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("❗ Usage: /contact <telegram_id> <message>")
        return

    try:
        user_id = int(args[1])
        reply_text = args[2]
        await bot.send_message(chat_id=user_id, text=f"📬 Support reply:\n\n{reply_text}")
        await message.answer("✅ Reply sent successfully.")
    except Exception as e:
        await message.answer(f"⚠️ Failed to send message: {e}")

# === Run ===
if __name__ == "__main__":
    try:
        print('Starting the bot')
        asyncio.run(dp.start_polling(bot))
    except KeyboardInterrupt:
        print('Bot stopped')
