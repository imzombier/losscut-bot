from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from flask import Flask

import asyncio
import threading
import os
import sys

# FIX WINDOWS EMOJI ERROR
sys.stdout.reconfigure(encoding='utf-8')

# BOT TOKEN FROM RENDER ENVIRONMENT
TOKEN = os.getenv("BOT_TOKEN")

# BOT
bot = Bot(token=TOKEN)

# DISPATCHER
dp = Dispatcher(storage=MemoryStorage())

# FLASK APP
app = Flask(__name__)

@app.route("/")
def home():
    return "LossCut Pro Bot Running ✅"

# STATES
class BetState(StatesGroup):
    amount = State()
    back_odds = State()

# START / HI / HELLO
@dp.message(CommandStart())
@dp.message(F.text.lower().in_(["hi", "hello", "hey"]))
async def start_bot(message: Message, state: FSMContext):

    await state.clear()

    text = (
        "🔥 Welcome To LossCut Pro Bot\n\n"
        "💰 Send Entry Stake Amount"
    )

    await message.answer(text)

    await state.set_state(BetState.amount)

# GET AMOUNT
@dp.message(BetState.amount)
async def get_amount(message: Message, state: FSMContext):

    try:
        amount = float(message.text)

        if amount <= 0:
            await message.answer(
                "❌ Enter valid amount"
            )
            return

        await state.update_data(amount=amount)

        await message.answer(
            "📈 Send Entry Back Odds\n\n"
            "Example : 3.0"
        )

        await state.set_state(BetState.back_odds)

    except:
        await message.answer(
            "❌ Send valid amount"
        )

# GET BACK ODDS
@dp.message(BetState.back_odds)
async def get_back_odds(message: Message, state: FSMContext):

    try:
        back_odds = float(message.text)

        if back_odds <= 1:
            await message.answer(
                "❌ Odds must be greater than 1"
            )
            return

        data = await state.get_data()

        amount = data["amount"]

        response = (
            f"🔥 LOSSCUT PRO ANALYSIS\n\n"

            f"💰 Entry Stake : ₹{amount:.0f}\n"
            f"📈 Entry Odds : {back_odds}\n\n"

            f"━━━━━━━━━━━━━━━━\n\n"

            f"🟢 PROFIT BOOK OPTIONS\n\n"
        )

        # GREEN BOOK
        lay_odds = round(back_odds - 1, 1)

        if lay_odds <= 1:
            lay_odds = 1.1

        while lay_odds < back_odds:

            lay_amount = (
                back_odds * amount
            ) / lay_odds

            profit = lay_amount - amount

            response += (
                f"🟢 {lay_odds:.1f} "
                f"→ Lay ₹{lay_amount:.0f} "
                f"→ +₹{profit:.0f}\n"
            )

            lay_odds += 0.1

        # SAFE EXIT
        response += (
            f"\n━━━━━━━━━━━━━━━━\n\n"
            f"🟡 SAFE EXIT OPTIONS\n\n"
        )

        zero_odds = round(back_odds, 1)

        for i in range(5):

            lay_amount = (
                back_odds * amount
            ) / zero_odds

            no_loss = lay_amount - amount

            response += (
                f"🟡 {zero_odds:.1f} "
                f"→ Lay ₹{lay_amount:.0f} "
                f"→ ₹{no_loss:.0f}\n"
            )

            zero_odds += 0.1

        # LOW LOSS
        response += (
            f"\n━━━━━━━━━━━━━━━━\n\n"
            f"🔴 RISK CONTROL\n\n"
        )

        low_loss_odds = round(back_odds + 0.5, 1)

        for i in range(5):

            lay_amount = (
                back_odds * amount
            ) / low_loss_odds

            loss = amount - lay_amount

            response += (
                f"🔴 {low_loss_odds:.1f} "
                f"→ Lay ₹{lay_amount:.0f} "
                f"→ -₹{loss:.0f}\n"
            )

            low_loss_odds += 0.2

        response += (
            f"\n━━━━━━━━━━━━━━━━\n"
            f"✅ Trade Smart • Hedge Smart\n"
            f"🤖 Powered By LossCut Pro"
        )

        await message.answer(response)

        await state.clear()

    except:
        await message.answer(
            "❌ Send valid odds"
        )

# TELEGRAM BOT POLLING
async def start_bot_polling():

    print("Bot Running...")

    # REMOVE WEBHOOK
    await bot.delete_webhook(
        drop_pending_updates=True
    )

    # START POLLING
    await dp.start_polling(bot)

# RUN BOT IN THREAD
def run_bot():

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    loop.run_until_complete(
        start_bot_polling()
    )

# MAIN
if __name__ == "__main__":

    # START TELEGRAM BOT
    threading.Thread(
        target=run_bot,
        daemon=True
    ).start()

    # START FLASK WEB SERVER
    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
