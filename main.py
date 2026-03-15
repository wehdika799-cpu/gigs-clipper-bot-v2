import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip

TOKEN = '8608143783:AAEpmfL6OrT5StZwhzLpkE2rkWJIvpWnBeo'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👾 Lab cvAI4 LITE Aktif!\nKirim link (YT, TikTok, IG, dll) & durasi.\nFormat: [Link] [Start] [End]")

async def process_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.split()
    if len(msg) < 3:
        await update.message.reply_text("❌ Format: Link Start End")
        return

    url, start_t, end_t = msg[0], msg[1], msg[2]
    chat_id = update.message.chat_id
    await update.message.reply_text("⏳ Mesin cvAI4 lagi nyedot video... Tunggu bentar Tuan.")

    raw_vid = f'raw_{chat_id}.mp4'
    final_vid = f'final_{chat_id}.mp4'

    try:
        # PENYAMARAN AGAR TIDAK ERROR 403
        ydl_opts = {
            'format': 'best',
            'outtmpl': raw_vid,
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.google.com/',
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        clip = VideoFileClip(raw_vid).subclip(start_t, end_t)
        w, h = clip.size
        target_w = h * (9/16)
        portrait_clip = clip.crop(x_center=w/2, width=target_w, height=h).resize(height=1280)
        portrait_clip.write_videofile(final_vid, codec="libx264", audio_codec="aac", fps=24, logger=None)

        with open(final_vid, 'rb') as video:
            await update.message.reply_video(video, caption="👑 Beres! Video dari jagat internet sudah diproses.")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Waduh Error: {str(e)}")
    
    if os.path.exists(raw_vid): os.remove(raw_vid)
    if os.path.exists(final_vid): os.remove(final_vid)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), process_video))
    app.run_polling()
