from base64 import b64encode
import io
import logging
from PIL import Image
import os
PORT = int(os.environ.get('PORT', 5000))

from dotenv import load_dotenv

load_dotenv(".env")
TOKEN = os.environ["BOT_TOKEN"]

from telegram import ReplyKeyboardRemove, constants, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from api_classifier import classify_image

from nearest import nearest

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


PHOTO, LOCATION = range(2)

RECYCEABLE_NOTES = {
    'discarded clothing': "❤️ Consider donating or selling so they can be reused! ",
    'food waste': "❌ Please dispose them in a normal bin, they <b>cannot</b> be recycled and will cause contamination. ", 
    'plastic bags': "✅ These can be recycled in a blue bin! But please make sure they are clean so they won't cause contamination. ", 
    'scrap metal pieces': "🏭 Please make sure they are clean and not too small or dangerous for workers to pick up. ", 
    'wood scraps': "🪵 These cannot be thrown in a normal recycling bin, please look for a specialised vendor or dispose as general waste. ", 
    "Recycleable Items": "These are recycleable items, but I am unable to tell what they are exactly. 😢", 

    "aluminium can": "✅ These can be recycled in a blue bin! But please make sure they are clean so they won't cause contamination. ", 
    "cardboard": "✅ These can be recycled in a blue bin! But please make sure they are clean so they won't cause contamination. ", 
    "glass": "✅ These can be recycled in a blue bin! But please make sure they are clean so they won't cause contamination. \nPlease also make sure they are all glass and not crystal glass or procelein! ", 
    "HDPE container": "✅ These can be recycled in a blue bin! But please make sure they are clean so they won't cause contamination. \nNote that food containers should not be recycled. ", 
    "paper": "✅ These can be recycled in a blue bin! But please make sure they are clean so they won't cause contamination. \nBut please do not recycle this if it was used to contain food. ", 
    "PET plastic bottle": "✅ These can be recycled in a blue bin! But please make sure they are clean so they won't cause contamination. \nBut please do not recycle this if it was used to contain food. ", 
    "steel and tin cans": "✅ These can be recycled in a blue bin! But please make sure they are clean so they won't cause contamination. \nBut please do not recycle this if it was used to contain food. "
}

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

    if success: 
        result = list(map(lambda x: f'<b>{x.capitalize()}</b>' + '\n' + RECYCEABLE_NOTES[x], result))
        res_str = '\n'.join(result)
        await update.message.reply_text(
                "You could be looking at:\n" + res_str, parse_mode=constants.ParseMode('HTML')
        )
    return ConversationHandler.END

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Please send me your location and I will show you the nearest recycling bins. ",
        reply_markup=ReplyKeyboardRemove(),
    )

    return LOCATION

def construct_location_line(d, addr): 
    return f"🔷 <b>{addr['ADDRESSBLO'] + ' ' + addr['ADDRESSBUI']}</b>" + '\n' + f"<b>{addr['ADDRESSSTR']}</b>" + '\n' + f"<b>Singapore {addr['ADDRESSPOS']}</b>" + '\n' + f"{addr['NAME']}" + '\n' + f"{str(round(d, 2))} km away"

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )

    nearest_bins = nearest(longitude=user_location.longitude, latitude=user_location.latitude)
    for d, addr in nearest_bins: 
        await update.message.reply_text(construct_location_line(d, addr), parse_mode=constants.ParseMode('HTML'))
        await update.message.reply_location(latitude=addr['LATITUDE'], longitude=addr['LONGITUDE'])
    lines = construct_location_line(nearest_bins)

    for k in lines: 
        await update.message.reply_text(lines[k], parse_mode=constants.ParseMode('HTML'))
        await update.message.reply_location()
    await update.message.reply_text(
        "\n\n".join(lines.values()), parse_mode=constants.ParseMode('HTML')
    )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! ", reply_markup=ReplyKeyboardRemove()
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
    # application.run_polling()

    # USE ON CLOUD
    application.run_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN, 
                          webhook_url="https://recycling-recognition.herokuapp.com/" + TOKEN)

if __name__ == "__main__":
    main()
