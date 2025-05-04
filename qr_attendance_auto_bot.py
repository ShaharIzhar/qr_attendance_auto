import pdb #debugger
import subprocess
import selenium
from telegram import Update
import os
import qr_reader
import webbrowser
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ConversationHandler, ContextTypes
)

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

#Setup Convo
global setup_completed
setup_completed = False

ASK_USERNAME, ASK_PASSWORD, ASK_PHOTO = range(3)

async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the best bot in Reichamn and the World! \nPlease enter Reichman's credientials - \nUsername:")
    return ASK_USERNAME

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["username"] = update.message.text
    first_name = extract_first_name_from_username(context.user_data["username"])
    await update.message.reply_text(f"Thanks {first_name}, Username Saved! What's your Password?")
    return ASK_PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global setup_completed
    context.user_data["password"] = update.message.text
    await update.message.reply_text(f"Password saved. Setup Complete. \nReady for next task.")
    setup_completed = True
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global setup_completed
    await update.message.reply_text("Conversation cancelled.")
    setup_completed = False
    return ConversationHandler.END

#image handler
async def upload_photo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global setup_completed
    if not(setup_completed):
        return await update.message.reply_text(f"Setup not completed yet. For initial Setup input /setup")

    context.user_data["awaiting_photo"] = True
    await update.message.reply_text("📸 Please upload a photo now.")

async def handle_uploaded_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global setup_completed
    if context.user_data.get("awaiting_photo") is not True:
        return  # Ignore photos unless they were asked for

    if not update.message.photo:
        await update.message.reply_text("⚠️ That's not a photo. Please send an image.")
        return

    # Save the photo
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = f"user_{update.message.from_user.id}_photo.jpg"
    await file.download_to_drive(file_path)

    context.user_data["photo_saved"] = True
    context.user_data["awaiting_photo"] = False

    await update.message.reply_text("✅ Photo received and saved successfully! Extracting URL:")
    if(context.user_data["photo_saved"]):
        data = qr_reader.detect_barcode_from_image(file_path)
        open_url_from_data(data)
    else: await update.message.reply_text("❌ No valid URL found in the QR code.")


#init
app = ApplicationBuilder().token(BOT_TOKEN).build() #setup
print("🤖 Bot is running...")

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("setup", setup)],
    states={
        ASK_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
        ASK_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
        ASK_PHOTO: [MessageHandler(filters.PHOTO & ~filters.COMMAND, upload_photo_command)],

    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

#general_commands
async def show_user_credientals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global setup_completed
    
    if(setup_completed):
        username = context.user_data["username"]
        password = context.user_data["password"]
        first_name = extract_first_name_from_username(username)
        await update.message.reply_text(f"✅ Credientals: \n First Name: {first_name} \n Username: {username} \n Password: {password} \n\n Ready for next command")
    else:
        await update.message.reply_text(f"⚠️ Setup not completed yet. For initial Setup input /setup")

# Add general command handlers
app.add_handler(CommandHandler("show_user_credientals", show_user_credientals))
app.add_handler(CommandHandler("upload", upload_photo_command))
app.add_handler(MessageHandler(filters.PHOTO, handle_uploaded_photo))

def extract_first_name_from_username(username):
    return username.split(".")[0].capitalize()

def open_url_from_data(data):
    if qr_reader.is_url(data):
            webbrowser.open(data)


app.add_handler(conv_handler)
app.run_polling()