import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip

# TOKEN LU YANG LAMA
TOKEN = '8608143783:AAEpmfL6OrT5StZwhzLpkE2rkWJIvpWnBeo'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👾 Lab cvAI4 LITE Aktif!\n\n"
        "Cara Pakai:\n"
        "Kirim link YouTube disertai durasi mulai dan selesai.\n"
        "Format: [Link] [Mulai] [Selesai]\n"
        "Contoh: https://youtu.be/abc 00:00:10 00:00:20"
    )

async def process_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_input = update.message.text.split()
    if len(text_input) < 3:
        await update.message.reply_text("❌ Format salah! Contoh: Link 00:10 00:20")
        return

    url = text_input[0]
    start_t = text_input[1]
    end_t = text_input[2]
    
    chat_id = update.message.chat_id
    await update.message.reply_text("⏳ Sedang memproses video menjadi vertikal... Sabar ya Tuan.")

    raw_vid = f'video_{chat_id}.mp4'
    final_vid = f'clip_{chat_id}.mp4'

    try:
        # Download Video
        ydl_opts = {'format': 'best[ext=mp4]', 'outtmpl': raw_vid, 'quiet': True}
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Edit Video ke Vertikal (9:16)
        clip = VideoFileClip(raw_vid).subclip(start_t, end_t)
        w, h = clip.size
        target_w = h * (9/16)
        
        # Crop tengah dan Resize ke 720p (Standar TikTok/Reels)
        final_clip = clip.crop(x_center=w/2, width=target_w, height=h).resize(height=1280)
        final_clip.write_videofile(final_vid, codec="libx264", audio_codec="aac", fps=24, logger=None)

        # Kirim ke Telegram
        with open(final_vid, 'rb') as video_file:
            await update.message.reply_video(video_file, caption="👑 Beres Tuan Gigs! Siap upload.")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Waduh Error: {str(e)}")
    
    # Hapus file sisa biar memori gak penuh
    if os.path.exists(raw_vid): os.remove(raw_vid)
    if os.path.exists(final_vid): os.remove(final_vid)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), process_video))
    print("Bot is running...")
    app.run_polling()
