import logging
import requests
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ContentType
from fastapi import FastAPI
import uvicorn

# Muhit o'zgaruvchilarini yuklash
API_TOKEN = os.getenv("BOT_TOKEN")
BACKEND_URL = "https://telegram-bot-api-hyyl.onrender.com/api/movie/"
WEBHOOK_URL = "https://telegram-bot-api-hyyl.onrender.com/webhook"
CHANNEL_USERNAME = "SNAYDERCOM"  # Kanal username

# Bot va dispatcher yaratish
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
app = FastAPI()

# API'ni uyg'otish funksiyasi (har 10 daqiqada)
async def keep_alive():
    while True:
        try:
            requests.get(f"{BACKEND_URL}/ping/")
            logging.info("✅ API ping yuborildi")
        except Exception as e:
            logging.error(f"❌ API ping yuborishda xatolik: {str(e)}")
        await asyncio.sleep(600)  # 10 daqiqada 1 marta

# Telegram webhook endpoint
@app.post("/webhook")
async def telegram_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)

# /start buyrug'i
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("🎬 Assalomu alaykum!\n\nUziningizga kerakli kino kodini kiriting🔒 ")

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
        "file_id": video_url,
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
    movie_id = message.text.strip()
    response = requests.get(f"{BACKEND_URL}{movie_id}/")

    if response.status_code == 200:
        data = response.json()
        file_id = data["file_id"]
        description = data["description"]
        await message.answer(f"{description} \n 📢 channel: ➡️  {file_id} KANALIMIZGA AZO BULSANGIZ XURSAND BULARDIK")
    else:
        await message.answer("❌ Bunday film topilmadi. Iltimos, to‘g‘ri ID kiriting.")

# Botni ishga tushirish va webhook sozlash
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)
    asyncio.create_task(keep_alive())  # API’ni uyg‘otish

if __name__ == "__main__":
    asyncio.run(on_startup())
    uvicorn.run(app, host="0.0.0.0", port=10000)
