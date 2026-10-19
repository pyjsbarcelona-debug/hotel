import asyncio
import logging
import json
import aiosqlite

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

BOT_TOKEN = "8937351582:AAEM5PSJNA3CDY0MY-BsN24JdO6RQEeTUDs"
ADMIN_IDS = [123456789]
DB_NAME = "hotel_booking.db"

# Replace with your deployed Web App URL (e.g., Vercel, Netlify, or GitHub Pages)
WEB_APP_URL = "https://pyjsbarcelona-debug.github.io/hotel/"

logging.basicConfig(level=logging.INFO)


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                full_name TEXT,
                phone TEXT,
                room_type TEXT,
                check_in_date TEXT,
                nights INTEGER,
                total_price REAL,
                status TEXT DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.commit()


async def save_booking(user_id: int, full_name: str, phone: str, room_type: str, check_in: str, nights: int,
                       total_price: float):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO bookings (user_id, full_name, phone, room_type, check_in_date, nights, total_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, full_name, phone, room_type, check_in, nights, total_price)
        )
        await db.commit()


dp = Dispatcher()


def main_menu_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏨 Open Hotel Mini App", web_app=WebAppInfo(url=WEB_APP_URL))],
            [InlineKeyboardButton(text="ℹ️ Hotel Info", callback_data="hotel_info")]
        ]
    )


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"👋 Welcome to **Grand Luxe Hotel**, {message.from_user.first_name}!\n\n"
        "Tap the button below to open our booking Mini App:",
        reply_markup=main_menu_kb(),
        parse_mode="Markdown"
    )


@dp.callback_query(F.data == "hotel_info")
async def process_info(callback: CallbackQuery):
    await callback.message.edit_text(
        "✨ **Grand Luxe Hotel** ✨\n\n"
        "📍 **Location**: 77 Luxury Ave, City Center\n"
        "⭐ **Rating**: 5-Star\n"
        "🏊‍♂️ **Amenities**: Free Wi-Fi, Pool, Spa, Gym, 24/7 Room Service.",
        reply_markup=main_menu_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()


# --- Handle Data Sent from HTML Mini App ---
@dp.message(F.web_app_data)
async def process_web_app_data(message: Message, bot: Bot):
    try:
        data = json.loads(message.web_app_data.data)

        full_name = data.get("full_name")
        phone = data.get("phone")
        room_type = data.get("room_type")
        check_in = data.get("check_in")
        nights = int(data.get("nights", 1))
        total_price = float(data.get("total_price", 0))

        # Save to database
        await save_booking(
            user_id=message.from_user.id,
            full_name=full_name,
            phone=phone,
            room_type=room_type,
            check_in=check_in,
            nights=nights,
            total_price=total_price
        )

        # Confirm to user
        await message.answer(
            "🎉 **Reservation Confirmed via Mini App!**\n\n"
            f"👤 Guest: {full_name}\n"
            f"📞 Phone: {phone}\n"
            f"🏨 Room: {room_type}\n"
            f"📅 Check-in: {check_in} ({nights} nights)\n"
            f"💳 Total: ${total_price}\n\n"
            "Our manager will contact you shortly.",
            reply_markup=main_menu_kb(),
            parse_mode="Markdown"
        )

        # Notify Admin
        admin_msg = (
            "🚨 **NEW MINI APP BOOKING**\n\n"
            f"👤 Guest: {full_name}\n"
            f"📞 Phone: {phone}\n"
            f"🏨 Room: {room_type}\n"
            f"📅 Date: {check_in} ({nights} nights)\n"
            f"💰 Total: ${total_price}"
        )
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(chat_id=admin_id, text=admin_msg, parse_mode="Markdown")
            except Exception as e:
                logging.error(f"Failed to notify admin: {e}")

    except Exception as e:
        await message.answer(f"⚠️ Error processing booking data: {e}")


async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    print("🚀 Hotel Bot with Mini App initialized...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

print("Press Ctrl+C to exit...")


def main():
    asyncio.run(main())


def counter():
    print("Counter is running...")
