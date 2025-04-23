import asyncio
import smtplib
from email.mime.text import MIMEText
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from dotenv import load_dotenv
import os

load_dotenv()

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
SMTP_EMAIL = os.getenv('SMTP_EMAIL')
TO_EMAIL = os.getenv('TO_EMAIL')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = 587
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

# === FSM States ===
class SupportForm(StatesGroup):
    waiting_for_question = State()

# === Email sender ===
def send_email(from_name, question, telegram_user):
    msg = MIMEText(f"Question from @{telegram_user.username or telegram_user.first_name}, #{telegram_user.id}:\n\n{question}")
    msg['Subject'] = "New Support Request"
    msg['From'] = SMTP_EMAIL
    msg['To'] = TO_EMAIL

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)

# === Bot setup ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# === Handlers ===

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer(
        "👋 Welcome to Support!\n\nPlease describe your issue or question, and include your email so we can get back to you. 💬",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(SupportForm.waiting_for_question)

@dp.message(SupportForm.waiting_for_question)
async def receive_question(message: Message, state: FSMContext):
    question = message.text
    send_email(from_name=message.from_user.full_name, question=question, telegram_user=message.from_user)

    await message.answer("✅ Your question has been sent! We'll get back to you as soon as possible.")
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
        print('bot is down')

