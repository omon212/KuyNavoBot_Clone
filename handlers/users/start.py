import re
import requests
import asyncio
import httpx
from aiogram import types
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
from loader import dp, bot
import logging
from handlers.users.download_instagram import download_instagram
from handlers.users.download_likee import download_likee
from handlers.users.download_pinterest import download_pinterest
from handlers.users.download_snapchat import download_snapchat
from handlers.users.download_threads import download_threads
from handlers.users.download_tiktok import download_tiktok
from handlers.users.download_youtube import download_youtube

RAPIDAPI_KEY = "4e3f34f7femsh7a9d112e3fee647p125284jsn050cb0333c97"
RAPIDAPI_HOST = "spotify-downloader9.p.rapidapi.com"

start_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔗 Send Link")],
    ],
    resize_keyboard=True
)

@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(
        """
<b>🔥 Assalomu alaykum. @kuynavobot ga Xush kelibsiz. Bot orqali quyidagilarni yuklab olishingiz mumkin:</b>

<b>• Instagram</b> - post va IGTV + audio bilan;
<b>• TikTok</b> - suv belgisiz video + audio bilan;
<b>• YouTube</b> - videolar va shorts + audio bilan;
<b>• Snapchat</b> - suv belgisiz video + audio bilan;
<b>• Likee</b> - suv belgisiz video + audio bilan;
<b>• Pinterest</b> - suv belgisiz video va rasmlar + audio bilan;
<b>• Threads</b> - video va rasmlar + audio bilan;

<b>Shazam funksiya:</b>
• Qo‘shiq nomi yoki ijrochi ismi

<b>🚀 Yuklab olmoqchi bo'lgan videoga havolani yuboring yoki qo'shiq nomini yozing!</b>
        """,
        parse_mode="HTML",
        reply_markup=start_button
    )

def is_url(text):
    url_pattern = re.compile(r'http[s]?://')
    return re.match(url_pattern, text) is not None

def get_spotify_song_download_url(song_name):
    url = "https://spotify-downloader9.p.rapidapi.com/downloadSong"
    querystring = {"songId": song_name}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    response = requests.get(url, headers=headers, params=querystring)
    return response.json() if response.status_code == 200 else None

async def search_song_on_itunes(song_name):
    url = "https://itunes.apple.com/search"
    params = {
        "term": song_name,
        "media": "music",
        "limit": 1
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
    return data["results"][0] if data["resultCount"] > 0 else None

@dp.message_handler()
async def handle_request(message: types.Message):
    text = message.text


    if is_url(text):
        await download_content(message)
    else:
        await handle_song_request(message)

async def download_content(message: types.Message):
    url = message.text
    regex_patterns = {
        "instagram": r'https:\/\/www\.instagram\.com\/(p|reel|reels)\/([A-Za-z0-9-_]+)\/',
        "tiktok": r'https:\/\/(www\.tiktok\.com\/@[\w]+\/video\/\d+(?:\?\S*)?|vt\.tiktok\.com\/[\w]+\/?)',
        "youtube": r'https:\/\/(www\.youtube\.com\/watch\?v=[\w-]+|youtu\.be\/[\w-]+|www\.youtube\.com\/shorts\/[\w-]+)',
        "snapchat": r'https:\/\/www\.snapchat\.com\/.*',
        "likee": r'https:\/\/likee\.video\/.*',
        "pinterest": r'https:\/\/(www\.pinterest\.com\/pin\/.*|pin\.it\/[A-Za-z0-9]+)',
        "threads": r'https:\/\/www\.threads\.net\/.*'
    }

    downloader_map = {
        "instagram": download_instagram,
        "tiktok": download_tiktok,
        "youtube": download_youtube,
        "snapchat": download_snapchat,
        "likee": download_likee,
        "pinterest": download_pinterest,
        "threads": download_threads,
    }

    matched_platform = next((platform for platform, pattern in regex_patterns.items() if re.search(pattern, url)), None)
    if matched_platform:
        content = await downloader_map[matched_platform](url)
        await send_media(content, message)
    else:
        await message.answer("⚠️ Yuklab olish uchun to'g'ri havola yuboring.")

async def send_media(content, message):
    try:
        if content.get("error") == False:
            msg = await message.answer('⏳ Iltimos kuting...')
            await asyncio.sleep(1)
            await msg.delete()

            media = content["medias"][0]
            if media["type"] == "image":
                await bot.send_photo(chat_id=message.chat.id, photo=media["url"])
            elif media["type"] == "video":
                await bot.send_video(chat_id=message.chat.id, video=media["url"])
        else:
            await message.answer("⚠️ Media yuklab bo'lmadi, havolani tekshiring yoki qayta urinib ko'ring.")
    except Exception as e:
        logging.error(f"Failed to send media: {e}")
        await message.answer("⚠️ Media yuklab olishda xatolik yuz berdi.")

@dp.message_handler()
async def handle_song_request(message: types.Message):
    song_name = message.text
    song_data = get_spotify_song_download_url(song_name)


    if not song_data or "downloadUrl" not in song_data:
        song_data = await search_song_on_itunes(song_name)
        if song_data:
            download_url = song_data.get("previewUrl")
            track_name = song_data.get("trackName", "Unknown Title")
            artist_name = song_data.get("artistName", "Unknown Artist")
        else:
            download_url = None
    else:
        download_url = song_data["downloadUrl"]
        track_name = song_data.get("title", "Unknown Title")
        artist_name = song_data.get("artist", "Unknown Artist")

    if download_url:

        message_text = "⏳ Iltimos kuting..."

        a = await message.answer(message_text, parse_mode="HTML")

        async with httpx.AsyncClient() as client:
            response = await client.get(download_url)
            original_audio = response.content

        with NamedTemporaryFile(suffix=".m4a") as temp_input, NamedTemporaryFile(suffix=".ogg") as temp_output:
            temp_input.write(original_audio)
            temp_input.flush()

            audio = AudioSegment.from_file(temp_input.name)
            audio.export(temp_output.name, format="ogg", codec="libopus")

            await a.delete()
            with open(temp_output.name, 'rb') as audio_file:
                await message.answer_audio(
                    audio_file,
                    title=track_name,
                    performer=artist_name,
                    duration=0,
                    caption=f"🎶 <b>{track_name}</b> - <i>{artist_name}</i>",
                    parse_mode="HTML"
                )
    else:
        await message.answer("⚠️ Couldn't retrieve the download URL. Please check the song name and try again.")