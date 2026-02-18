add main file
import os, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from database import init_db, save_order, update_status
from utils import generate_order_id, expiry_timer

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Select Service:", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Game Recharge", callback_data="service_game")]
    ]))

async def service_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    context.user_data["service"] = "Game Recharge"
    await query.message.reply_text("Select Game:", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Free Fire", callback_data="game_ff")]
    ]))

async def game_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    context.user_data["game"] = "Free Fire"
    await query.message.reply_text("Send your Game ID:")

async def user_id_handler(update: Update, context):
    uid = update.message.text
    order_id = generate_order_id()
    context.user_data["order_id"] = order_id
    save_order(order_id, update.message.chat_id,
               context.user_data["service"],
               context.user_data["game"])
    await update.message.reply_text(
        f"💳 Pay via QR\nOrder ID: {order_id}\nSend screenshot within 5 minutes.")
    asyncio.create_task(expiry_timer(context.bot, update.message.chat_id, order_id, __import__("database")))

async def screenshot_handler(update: Update, context):
    order_id = context.user_data.get("order_id")
    if not order_id: return
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Approve", callback_data=f"ap_{order_id}"),
         InlineKeyboardButton("❌ Reject", callback_data=f"rj_{order_id}")]
    ])
    await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id,
                                 caption=f"Order {order_id}", reply_markup=kb)
    await update.message.reply_text("📤 Screenshot sent for verification.")

async def admin_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    action, oid = query.data.split("_")
    status = "APPROVED" if action=="ap" else "REJECTED"
    update_status(oid, status)
    await query.edit_message_caption(f"Order {oid} → {status}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(service_handler, pattern="service_"))
app.add_handler(CallbackQueryHandler(game_handler, pattern="game_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_id_handler))
app.add_handler(MessageHandler(filters.PHOTO, screenshot_handler))
app.add_handler(CallbackQueryHandler(admin_handler, pattern="ap_|rj_"))

app.run_polling()
