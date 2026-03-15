import PIL.Image
# PATCH KHUSUS: Paksa ANTIALIAS pake LANCZOS biar gak error di Python 3.13
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip

# TOKEN LU
TOKEN = '8608143783:AAEpmfL6OrT5StZwhzLpkE2rkWJIvpWnBeo'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👾 Lab cvAI4 LITE Aktif (Anti-Error Version)!\n\n"
        "Format: [Link] [Mulai] [Selesai]\n"
        "Contoh: https://vt.tiktok.com/xxx 00:00:00 00:00:05"
    )

async def process_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_input = update.message.text.split()
    if len(text_input) < 3:
        await update.message.reply_text("❌ Format: Link 00:00 00:05")
        return

    url, start_t, end_t = text_input[0], text_input[1], text_input[2]
    chat_id = update.message.chat_id
    await update.message.reply_text("⏳ Mesin cvAI4 lagi kerja... Tunggu bentar Tuan.")

    raw_vid = f'video_{chat_id}.mp4'
    final_vid = f'clip_{chat_id}.mp4'

    try:
        # Download dengan penyamaran agar tidak Error 403
        ydl_opts = {
            'format': 'best',
            'outtmpl': raw_vid,
            'quiet': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Proses Editing Vertikal
        clip = VideoFileClip(raw_vid).subclip(start_t, end_t)
        w, h = clip.size
        target_w = h * (9/16)
        
        # Crop tengah dan Resize
        final_clip = clip.crop(x_center=w/2, width=target_w, height=h).resize(height=1280)
        final_clip.write_videofile(final_vid, codec="libx264", audio_codec="aac", fps=24, logger=None)

        # Kirim ke Tuan
        with open(final_vid, 'rb') as video_file:
            await update.message.reply_video(video_file, caption="👑 Beres Tuan Gigs! Hasil rapi jali.")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Waduh Error: {str(e)}")
    
    # Bersihkan sampah
    if os.path.exists(raw_vid): os.remove(raw_vid)
    if os.path.exists(final_vid): os.remove(final_vid)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), process_video))
    print("Bot Gigs Aktif...")
    app.run_polling()
