from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from flask import Flask, render_template_string

import asyncio
import threading
import os
import sys

# =========================
# FIX WINDOWS EMOJI ERROR
# =========================

sys.stdout.reconfigure(encoding='utf-8')

# =========================
# BOT TOKEN
# =========================

TOKEN = os.getenv("BOT_TOKEN")

# =========================
# BOT
# =========================

bot = Bot(token=TOKEN)

# =========================
# DISPATCHER
# =========================

dp = Dispatcher(storage=MemoryStorage())

# =========================
# FLASK APP
# =========================

app = Flask(__name__)

# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():

    return """
    <h2 style='font-family:Arial;text-align:center;
    margin-top:50px;'>
    ✅ LossCut Pro Bot Running
    </h2>
    """

# =========================
# DONATION PAGE
# =========================

@app.route("/donate")
def donate():

    html = """

    <!DOCTYPE html>

    <html>

    <head>

        <title>Support LossCut Pro</title>

        <meta name="viewport"
        content="width=device-width, initial-scale=1.0">

        <style>

            body{
                background:#0f172a;
                font-family:Arial;
                text-align:center;
                color:white;
                padding:20px;
            }

            .card{
                background:#1e293b;
                max-width:420px;
                margin:auto;
                padding:25px;
                border-radius:20px;
                box-shadow:0 0 20px rgba(0,0,0,0.4);
            }

            h1{
                color:#22c55e;
            }

            p{
                color:#cbd5e1;
                line-height:1.7;
            }

            img{
                width:260px;
                border-radius:20px;
                border:5px solid white;
                margin-top:20px;
                margin-bottom:20px;
            }

            .btn{
                display:block;
                width:90%;
                margin:12px auto;
                padding:15px;
                border-radius:12px;
                text-decoration:none;
                font-size:18px;
                font-weight:bold;
                color:white;
            }

            .gpay{
                background:#4285F4;
            }

            .phonepe{
                background:#5f259f;
            }

            .paytm{
                background:#00b9f5;
            }

        </style>

    </head>

    <body>

        <div class="card">

            <h1>🤲 Help Poor People</h1>

            <p>
            Your support helps for poor people ❤️
            </p>

            <!-- QR IMAGE -->

            <img src="/photo_2026-05-21_07-06-33.jpg">

            <!-- GPay -->

            <a class="btn gpay"
            href="upi://pay?pa=Q398862448@ybl&pn=GKSolutions&cu=INR">

            💚 Pay Using Google Pay

            </a>

            <!-- PhonePe -->

            <a class="btn phonepe"
            href="upi://pay?pa=Q398862448@ybl&pn=GKSolutions&cu=INR">

            💜 Pay Using PhonePe

            </a>

            <!-- Paytm -->

            <a class="btn paytm"
            href="upi://pay?pa=Q398862448@ybl&pn=GKSolutions&cu=INR">

            💙 Pay Using Paytm

            </a>

        </div>

    </body>

    </html>

    """

    return render_template_string(html)

# =========================
# STATES
# =========================

class BetState(StatesGroup):

    bet_type = State()

    amount = State()

    odds = State()

# =========================
# START / HI / HELLO
# =========================

@dp.message(CommandStart())
@dp.message(F.text.lower().in_(["hi", "hello", "hey"]))
async def start_bot(
    message: Message,
    state: FSMContext
):

    await state.clear()

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📈 BACK",
                    callback_data="back"
                ),

                InlineKeyboardButton(
                    text="📉 LAY",
                    callback_data="lay"
                )
            ]
        ]
    )

    await message.answer(
        "🔥 Welcome To LossCut Pro Bot\n\n"
        "🛡️ I Will Helps You Reduce Losses & Secure Profits\n\n"

        "📌 Select Bet Type Below",
        reply_markup=buttons
    )

# =========================
# BACK BUTTON
# =========================

@dp.callback_query(F.data == "back")
async def back_button(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.update_data(
        bet_type="BACK"
    )

    await callback.message.answer(
        "💰 Send BACK Stake Amount"
    )

    await state.set_state(
        BetState.amount
    )

    await callback.answer()

# =========================
# LAY BUTTON
# =========================

@dp.callback_query(F.data == "lay")
async def lay_button(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.update_data(
        bet_type="LAY"
    )

    await callback.message.answer(
        "💰 Send LAY Stake Amount"
    )

    await state.set_state(
        BetState.amount
    )

    await callback.answer()

# =========================
# GET AMOUNT
# =========================

@dp.message(BetState.amount)
async def get_amount(
    message: Message,
    state: FSMContext
):

    try:

        amount = float(message.text)

        if amount <= 0:

            await message.answer(
                "❌ Enter valid amount"
            )

            return

        await state.update_data(
            amount=amount
        )

        data = await state.get_data()

        bet_type = data["bet_type"]

        await message.answer(
            f"📈 Send {bet_type} Odds\n\n"
            f"Example : 5"
        )

        await state.set_state(
            BetState.odds
        )

    except:

        await message.answer(
            "❌ Send valid amount"
        )

# =========================
# GET ODDS
# =========================

@dp.message(BetState.odds)
async def get_odds(
    message: Message,
    state: FSMContext
):

    try:

        odds = float(message.text)

        if odds <= 1:

            await message.answer(
                "❌ Odds must be greater than 1"
            )

            return

        data = await state.get_data()

        amount = data["amount"]

        bet_type = data["bet_type"]

        if bet_type == "BACK":

            entry_profit = (
                (odds - 1) * amount
            )

            calc_type = "LAY"

        else:

            entry_profit = amount

            calc_type = "BACK"

        response = (
            f"🔥 LOSSCUT PRO ANALYSIS\n\n"

            f"📊 Entry Type : {bet_type}\n"
            f"💰 Entry Stake : ₹{amount:.0f}\n"
            f"📈 Entry Odds : {odds:.1f}\n"
            f"🏆 Entry Win Profit : ₹{entry_profit:.0f}\n\n"

            f"━━━━━━━━━━━━━━━━\n\n"
        )

        # =========================
        # PROFIT BOOK
        # =========================

        response += (
            f"🟢 {calc_type} PROFIT BOOK\n\n"
        )

        results = 10

        if bet_type == "BACK":

            start = 1.1

        else:

            start = 1.2

        end = odds

        step = (
            (end - start)
            / (results - 1)
        )

        current = start

        for i in range(results):

            try:

                if bet_type == "BACK":

                    hedge_amount = (
                        odds * amount
                    ) / current

                else:

                    hedge_amount = (
                        (odds - 1) * amount
                    ) / (current - 1)

                profit = (
                    hedge_amount - amount
                )

                response += (
                    f"🟢 {current:.1f} "
                    f"→ {calc_type} ₹{hedge_amount:.0f} "
                    f"→ +₹{profit:.0f}\n"
                )

            except:
                pass

            current += step

        # =========================
        # SAFE EXIT
        # =========================

        response += (
            f"\n━━━━━━━━━━━━━━━━\n\n"
            f"🟡 SAFE EXIT OPTIONS\n\n"
        )

        safe_start = odds + 0.1

        safe_end = odds + 2

        safe_step = (
            (safe_end - safe_start)
            / 9
        )

        current_safe = safe_start

        for i in range(10):

            try:

                if bet_type == "BACK":

                    hedge_amount = (
                        odds * amount
                    ) / current_safe

                else:

                    hedge_amount = (
                        (odds - 1) * amount
                    ) / (current_safe - 1)

                safe_result = (
                    hedge_amount - amount
                )

                response += (
                    f"🟡 {current_safe:.1f} "
                    f"→ {calc_type} ₹{hedge_amount:.0f} "
                    f"→ ₹{safe_result:.0f}\n"
                )

            except:
                pass

            current_safe += safe_step

        # =========================
        # RISK CONTROL
        # =========================

        response += (
            f"\n━━━━━━━━━━━━━━━━\n\n"
            f"🔴 RISK CONTROL\n\n"
        )

        risk_start = odds + 2.1

        risk_end = odds + 10

        risk_step = (
            (risk_end - risk_start)
            / 9
        )

        current_risk = risk_start

        for i in range(10):

            try:

                if bet_type == "BACK":

                    hedge_amount = (
                        odds * amount
                    ) / current_risk

                else:

                    hedge_amount = (
                        (odds - 1) * amount
                    ) / (current_risk - 1)

                loss = (
                    amount - hedge_amount
                )

                response += (
                    f"🔴 {current_risk:.1f} "
                    f"→ {calc_type} ₹{hedge_amount:.0f} "
                    f"→ -₹{loss:.0f}\n"
                )

            except:
                pass

            current_risk += risk_step

        # =========================
        # FOOTER
        # =========================

        response += (
            f"\n━━━━━━━━━━━━━━━━\n"
            f"✅ Trade Smart • Hedge Smart\n"
            f"🤖 Powered By LossCut Pro"
        )

        # =========================
        # DONATE BUTTON
        # =========================

        donate_buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🤲 Help Poor People",
                        url="https://losscut-bot.onrender.com/donate"
                    )
                ]
            ]
        )

        await message.answer(
            response,
            reply_markup=donate_buttons
        )

        await state.clear()

    except Exception as e:

        print(e)

        await message.answer(
            "❌ Send valid odds"
        )

# =========================
# TELEGRAM BOT POLLING
# =========================

async def start_bot_polling():

    print("Bot Running...")

    await bot.delete_webhook(
        drop_pending_updates=True
    )

    await dp.start_polling(
        bot,
        handle_signals=False
    )

# =========================
# RUN BOT THREAD
# =========================

def run_bot():

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    loop.run_until_complete(
        start_bot_polling()
    )

# =========================
# MAIN
# =========================

if __name__ == "__main__":

    threading.Thread(
        target=run_bot,
        daemon=True
    ).start()

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
