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

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_IDS = [123456789]  # O'z Telegram ID raqamingizni yozing
DB_NAME = "hotel_booking.db"

# Xostingga joylagan index.html manzilingizni shu yerga yozing
WEB_APP_URL = "https://your-hosted-webapp-url.com/index.html"

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
                status TEXT DEFAULT 'CONFIRMED',
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
            [InlineKeyboardButton(text="🏨 Mehmonxona Mini App", web_app=WebAppInfo(url=WEB_APP_URL))],
            [InlineKeyboardButton(text="ℹ️ Mehmonxona haqida", callback_data="hotel_info")]
        ]
    )


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"✨ **Grand Luxe Hotel**ga xush kelibsiz, {message.from_user.first_name}!\n\n"
        "Xona band qilish uchun quyidagi tugmani bosing:",
        reply_markup=main_menu_kb(),
        parse_mode="Markdown"
    )


@dp.callback_query(F.data == "hotel_info")
async def process_info(callback: CallbackQuery):
    await callback.message.edit_text(
        "🌟 **Grand Luxe Hotel Ma'lumotlari**\n\n"
        "📍 **Manzil**: Markaziy ko'cha, 77-uy\n"
        "⭐ **Daraja**: 5 Yulduzli\n"
        "🏊‍♂️ **Qulayliklar**: Bepul Wi-Fi, Basseyn, Spa, Fitnes va 24/7 xizmat.",
        reply_markup=main_menu_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()


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

        # Ma'lumotlar bazasiga saqlash
        await save_booking(
            user_id=message.from_user.id,
            full_name=full_name,
            phone=phone,
            room_type=room_type,
            check_in=check_in,
            nights=nights,
            total_price=total_price
        )

        # Foydalanuvchiga tasdiqnoma yuborish
        await message.answer(
            "🎉 **Buyurtmangiz muvaffaqiyatli qabul qilindi!**\n\n"
            f"👤 Mehmon: `{full_name}`\n"
            f"📞 Telefon: `{phone}`\n"
            f"🏨 Xona: `{room_type}`\n"
            f"📅 Kelish sanasi: `{check_in}` ({nights} kecha)\n"
            f"💳 Umumiy narx: **${total_price}**\n\n"
            "Tez orada menejerimiz siz bilan bog'lanadi.",
            reply_markup=main_menu_kb(),
            parse_mode="Markdown"
        )

        # Adminlarga xabar yuborish
        admin_msg = (
            "🚨 **YANGI BUYURTMA (Mini App)**\n\n"
            f"👤 Mehmon: {full_name}\n"
            f"📞 Tel: {phone}\n"
            f"🏨 Xona: {room_type}\n"
            f"📅 Sana: {check_in} ({nights} kecha)\n"
            f"💰 Narx: ${total_price}"
        )
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(chat_id=admin_id, text=admin_msg, parse_mode="Markdown")
            except Exception as e:
                logging.error(f"Adminni ogohlantirishda xatolik: {e}")

    except Exception as e:
        await message.answer(f"⚠️ Xatolik yuz berdi: {e}")


async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    print("🚀 Super Hotel Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
