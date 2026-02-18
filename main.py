import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

from database import init_db, save_order, update_status
from utils import generate_order_id, expiry_timer

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

init_db()

# ---------- USER FLOW ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🎮 Game Recharge", callback_data="service_game")]]
    await update.message.reply_text("Select Service:", reply_markup=InlineKeyboardMarkup(kb))

async def service_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["service"] = "Game Recharge"

    kb = [[InlineKeyboardButton("🔥 Free Fire", callback_data="game_ff")]]
    await query.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup(kb))

async def game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["game"] = "Free Fire"
    await query.message.reply_text("Send your Game ID:")

async def user_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text
    order_id = generate_order_id()
    context.user_data["order_id"] = order_id

    save_order(
        order_id,
        update.message.chat_id,
        context.user_data.get("service"),
        context.user_data.get("game")
    )

    await update.message.reply_text(
        f"💳 Pay via QR\n\n🆔 Order ID: {order_id}\n\nSend screenshot within 5 minutes."
    )

    asyncio.create_task(
        expiry_timer(context.bot, update.message.chat_id, order_id, __import__("database"))
    )

async def screenshot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order_id = context.user_data.get("order_id")
    if not order_id:
        return

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"ap_{order_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"rj_{order_id}")
        ]
    ])

    await context.bot.send_photo(
        ADMIN_ID,
        update.message.photo[-1].file_id,
        caption=f"Order {order_id}",
        reply_markup=kb
    )

    await update.message.reply_text("📤 Screenshot sent for verification.")

# ---------- ADMIN
