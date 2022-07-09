from base64 import b64encode
import io
import logging
from PIL import Image
import os
PORT = int(os.environ.get('PORT', 5000))

from dotenv import load_dotenv

load_dotenv(".env")
TOKEN = os.environ["BOT_TOKEN"]

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from api_classifier import classify_image

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


GENDER, PHOTO, LOCATION, BIO = range(4)


async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text(
        "Please send me a photo of your trash. ",
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()

    img_buffer = io.BytesIO()

    await photo_file.download(out=img_buffer)

    img = Image.open(img_buffer)
    img.thumbnail((256, 256))
    
    buff = io.BytesIO()
    img.save(buff, format="JPEG")
    img_str = b64encode(buff.getvalue())

    encoded = img_str.decode("utf-8")

    success, result = await classify_image(encoded)

    await update.message.reply_text(
        f"You are looking at {str(result)}. " if success else result
    )

    return ConversationHandler.END

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Please send me your location. ",
        reply_markup=ReplyKeyboardRemove(),
    )

    return LOCATION

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    await update.message.reply_text(
        f"Your location is {user_location}. "
    )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("photo", get_photo), CommandHandler("location", get_location)],
        states={
            PHOTO: [MessageHandler(filters.PHOTO, photo)],
            LOCATION: [MessageHandler(filters.LOCATION, location)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    # USE WHEN TESTING LOCALLY
    application.run_polling()

    # USE ON CLOUD
    # application.run_webhook(listen="0.0.0.0",
    #                       port=int(PORT),
    #                       url_path=TOKEN, 
    #                       webhook_url="https://recycling-recognition.herokuapp.com/" + TOKEN)

if __name__ == "__main__":
    main()
