import os
import PIL.Image
# Fix buat Python versi baru
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip

TOKEN = '8608143783:AAEpmfL6OrT5StZwhzLpkE2rkWJIvpWnBeo'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👾 Lab cvAI4 Aktif!\nKirim: [Link] [Start] [End]")

async def process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = update.message.text.split()
    if len(cmd) < 3: return
    
    url, s, e = cmd[0], cmd[1], cmd[2]
    chat_id = update.message.chat_id
    await update.message.reply_text("⏳ Sedang memproses video...")

    try:
        # Download
        with YoutubeDL({'format':'best','outtmpl':f'v_{chat_id}.mp4','quiet':True}) as ydl:
            ydl.download([url])

        # Edit
        clip = VideoFileClip(f'v_{chat_id}.mp4').subclip(s, e)
        w, h = clip.size
        # Crop Tengah (9:16)
        final = clip.crop(x_center=w/2, width=h*(9/16), height=h).resize(height=1280)
        final.write_videofile(f'f_{chat_id}.mp4', codec="libx264", audio_codec="aac", fps=24, logger=None)

        # Kirim
        with open(f'f_{chat_id}.mp4', 'rb') as f:
            await update.message.reply_video(f)

    except Exception as err:
        await update.message.reply_text(f"❌ Error: {str(err)}")

    # Bersih-bersih
    for f in [f'v_{chat_id}.mp4', f'f_{chat_id}.mp4']:
        if os.path.exists(f): os.remove(f)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), process))
    app.run_polling()
