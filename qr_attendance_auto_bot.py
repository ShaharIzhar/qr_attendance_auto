import subprocess

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import pdb

BOT_TOKEN = "7705872115:AAHiEY5XeAL2pxwwEm1Ex2xIPp13msA8ssk"


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1] 
    file = await photo.get_file()
    await file.download_to_drive("qr_photo.jpg")

async def runi_auth_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Hey! Please enter credientials for initial setup: ")
async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Upload QR photo")
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("runi_auth_init", runi_auth_init))
app.add_handler(CommandHandler("image", image))


#init
print("🤖 Bot is running...")
app.run_polling()