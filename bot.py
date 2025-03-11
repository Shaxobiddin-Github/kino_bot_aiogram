import logging
import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ContentType

API_TOKEN = "7775904021:AAFZZTv9DYwJMUXeKsBCNXznkDYchWbNT2o"
BACKEND_URL = "http://127.0.0.1:8000/api/movie/"
CHANNEL_USERNAME = "SNAYDERCOM"  # Kanal username

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# /start buyrug'i
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("🎬 Assalomu alaykum!\n\nuzingizga kerakli kino kodini kiriting🔒 ")

# Video yuborilganda (bazaga saqlash uchun)
@dp.message(lambda msg: msg.content_type == ContentType.VIDEO)
async def handle_incoming_video(message: types.Message):
    message_id = message.message_id
    video_url = f"https://t.me/{CHANNEL_USERNAME}/{message_id}"  # file_id sifatida URL

    await message.reply(
        "✅ Video qabul qilindi!\n"
        f"Quyidagi **file_id** (URL) ni bazaga saqlang:\n\n"
        f"`{video_url}`",
        parse_mode="Markdown"
    )

    # Backendga saqlash
    payload = {
        "title": f"Movie {message_id}",
        "movie_id": f"movie_{message_id}",
        "file_id": video_url,  # file_id ga URL saqlanadi
        "description": "Video description"
    }
    try:
        response = requests.post(BACKEND_URL, json=payload)
        if response.status_code == 201:
            await message.reply("✅ Ma'lumotlar bazaga saqlandi!")
        else:
            await message.reply(f"❌ Bazaga saqlashda xatolik: {response.text}")
    except Exception as e:
        await message.reply(f"❌ Xatolik yuz berdi: {str(e)}")

# Movie ID kiritilganda file_id qaytarish
@dp.message()
async def send_movie(message: types.Message):
    movie_id = message.text.strip()  # Foydalanuvchi kiritgan kod (movie_id)
    response = requests.get(f"{BACKEND_URL}{movie_id}/")

    if response.status_code == 200:
        data = response.json()
        file_id = data["file_id"]  # file_id ni olish (URL)
        description = data["description"]
        await message.answer(f"{description} \n 📢 channel: ➡️  {file_id} KANALIMIZGA AZO BULSANGIZ XURSAND BULARDIK")  # Faqat file_id qaytariladi
        

    else:
        await message.answer("❌ Bunday film topilmadi. Iltimos, to‘g‘ri ID kiriting.")

async def main():
    print("Bot ishga tushdi... 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())