add utils file 
import uuid, asyncio

def generate_order_id():
    return str(uuid.uuid4())[:8].upper()

async def expiry_timer(bot, chat_id, order_id, database, seconds=300):
    await asyncio.sleep(seconds)
    database.update_status(order_id, "EXPIRED")
    await bot.send_message(chat_id, f"⏳ Order {order_id} expired. Payment not received.")
