import PIL.Image
# PATCH: Mengatasi hilangnya ANTIALIAS di Python versi terbaru
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL
# PATH IMPORT STABIL: Mengatasi ModuleNotFoundError 'moviepy.editor'
from moviepy.video.io.VideoFileClip import VideoFileClip
import moviepy.video.fx.all as vfx

# TOKEN BOT
TOKEN = '8608143783:AAEpmfL6OrT5StZwhzLpkE2rkWJIvpWnBeo'

# Set up logging untuk memantau error di Railway Logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👾 Lab cvAI4 LITE Aktif (Fixed Version)!\n\n"
        "Format: [Link] [Mulai] [Selesai]\n"
        "Contoh: https://vt.tiktok.com/xxx 00:00:00 00:00:05"
    )

async def process_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_input = update.message.text.split()
    if len(text_input) < 3:
        await update.message.reply_text("❌ Format salah! Contoh: Link 00:00:00 00:00:05")
        return

    url, start_t, end_t = text_input[0], text_input[1], text_input[2]
    chat_id = update.message.chat_id
    await update.message.reply_text("⏳ Sedang memproses... Mesin cvAI4 mulai bekerja.")

    raw_vid = f'video_{chat_id}.mp4'
    final_vid = f'clip_{chat_id}.mp4'

    try:
        # Konfigurasi Download Anti-Blokir
        ydl_opts = {
            'format': 'best',
            'outtmpl': raw_vid,
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Proses Potong & Ubah ke Vertikal
        with VideoFileClip(raw_vid) as clip:
            sub_clip = clip.subclip(start_t, end_t)
            w, h = sub_clip.size
            target_w = h * (9/16)
            
            # Crop bagian tengah agar fokus
            final_clip = sub_clip.crop(x_center=w/2, width=target_w, height=h).resize(height=1280)
            final_clip.write_videofile(final_vid, codec="libx264", audio_codec="aac", fps=24, logger=None)

        # Kirim hasil akhir
        with open(final_vid, 'rb') as video_file:
            await update.message.reply_video(video_file, caption="👑 Beres! Video sudah siap di-upload.")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Waduh Error: {str(e)}")
    
    # Hapus file sementara agar storage tidak penuh
    if os.path.exists(raw_vid): os.remove(raw_vid)
    if os.path.exists(final_vid): os.remove(final_vid)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), process_video))
    print("Bot cvAI4 Running...")
    app.run_polling()
