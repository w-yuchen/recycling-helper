from base64 import b64encode
import io
import logging
from turtle import up
from PIL import Image
import os

PORT = int(os.environ.get('PORT', 5000))
import json
from dotenv import load_dotenv

load_dotenv(".env")
TOKEN = os.environ["BOT_TOKEN"]

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, constants, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

from api_classifier import classify_image

from nearest import SECONDHAND, nearest_bin, nearest_secondhand

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

PHOTO, LOCATION, SECONDHAND = range(3)

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data="1"),
            InlineKeyboardButton("Option 2", callback_data="2"),
        ],
        [InlineKeyboardButton("Option 3", callback_data="3")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    addr = query.data
    if addr['type'] == 0: 
        await query.edit_message_text(construct_location_line(addr), parse_mode=constants.ParseMode('HTML'))
        await context.bot.send_location(chat_id=context._chat_id, latitude=addr['LATITUDE'], longitude=addr['LONGITUDE'])
    else: 
        await query.edit_message_text(construct_location_line2(addr), parse_mode=constants.ParseMode('HTML'))
        await context.bot.send_location(chat_id=context._chat_id, latitude=addr['LATITUDE'], longitude=addr['LONGITUDE'])

# async def button2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Parses the CallbackQuery and updates the message text."""
#     query = update.callback_query

#     # CallbackQueries need to be answered, even if no notification to the user is needed
#     # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
#     await query.answer()
#     addr = query.data
#     await query.edit_message_text(construct_location_line2(addr), parse_mode=constants.ParseMode('HTML'))
#     await context.bot.send_location(chat_id=context._chat_id, latitude=addr['LATITUDE'], longitude=addr['LONGITUDE'])

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

    success, res = await classify_image(encoded)

    if success: 
        result = list(map(lambda x: f'<b>{x.capitalize()}</b>' + '\n' + RECYCEABLE_NOTES[x], res))
        res_str = '\n'.join(result)
        await update.message.reply_text(
                "You could be looking at:\n" + res_str, parse_mode=constants.ParseMode('HTML')
        )
        if 'discarded clothing' in res: 
            await context.bot.send_message(chat_id=context._chat_id, text="For old clothes, if you wish to sell them, you can use /secondhand command to find the nearest collection centres near you! ")
        await context.bot.send_message(chat_id=context._chat_id, text="You can use /recycling command to find the nearest recycling bins near you! ")

    return ConversationHandler.END

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Please send me your location and I will show you the nearest recycling bins. ",
        reply_markup=ReplyKeyboardRemove(),
    )

    return LOCATION

async def get_location_second_hand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Please send me your location and I will show you the nearest used goods collectors. ",
        reply_markup=ReplyKeyboardRemove(),
    )

    return SECONDHAND


def construct_location_line(addr): 
    return f"🔷 <b>{addr['ADDRESSBLO'] + ' ' + addr['ADDRESSBUI']}</b>" + '\n' + f"<b>{addr['ADDRESSSTR']}</b>" + '\n' + f"<b>Singapore {addr['ADDRESSPOS']}</b>"

def construct_location_line2(addr): 
    return f"🔷 <b>{addr['ADDRESSBUILDINGNAME']}</b>" + '\n' + f"<b>{addr['ADDRESSBLOCKHOUSENUMBER']} {addr['ADDRESSSTREETNAME']}</b>" + '\n' + f"<b>Singapore {addr['ADDRESSPOSTALCODE']}</b>" + '\n' + f"{addr['NAME']}" + '\n' + f"{addr['DESCRIPTION']}"

async def second_hand_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )

    nearest_secondhand_shops = nearest_secondhand(longitude=user_location.longitude, latitude=user_location.latitude)
    keyboard = []
    for d, addr in nearest_secondhand_shops: 
        print(json.dumps(addr))
        addr['type'] = 1
        keyboard.append([InlineKeyboardButton(f'{round(d, 2)}km away', callback_data=addr)])
        # await update.message.reply_text(construct_location_line(d, addr), parse_mode=constants.ParseMode('HTML'))
        # await update.message.reply_location(latitude=addr['LATITUDE'], longitude=addr['LONGITUDE'])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose recycling bin to view location:", reply_markup=reply_markup)

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )

    nearest_bins = nearest_bin(longitude=user_location.longitude, latitude=user_location.latitude)
    keyboard = []
    for d, addr in nearest_bins: 
        print(json.dumps(addr))
        addr['type'] = 0
        keyboard.append([InlineKeyboardButton(f'{round(d, 2)}km away', callback_data=addr)])
        # await update.message.reply_text(construct_location_line(d, addr), parse_mode=constants.ParseMode('HTML'))
        # await update.message.reply_location(latitude=addr['LATITUDE'], longitude=addr['LONGITUDE'])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose recycling bin to view location:", reply_markup=reply_markup)

    # keyboard = [
    #     [
    #         InlineKeyboardButton("Option 1", callback_data=(addr['LATITUDE'], addr['LONGITUDE']), ),
    #         InlineKeyboardButton("Option 2", callback_data="2"),
    #     ],
    #     [InlineKeyboardButton("Option 3", callback_data="3")],
    # ]

    # for k in lines: 
    #     await update.message.reply_text(lines[k], parse_mode=constants.ParseMode('HTML'))
    #     await update.message.reply_location()
    # await update.message.reply_text(
    #     "\n\n".join(lines.values()), parse_mode=constants.ParseMode('HTML')
    # )

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
    application = Application.builder().token(TOKEN).arbitrary_callback_data(True).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("photo", get_photo), CommandHandler("recycling", get_location), CommandHandler("secondhand", get_location_second_hand)],
        states={
            PHOTO: [MessageHandler(filters.PHOTO, photo)],
            LOCATION: [MessageHandler(filters.LOCATION, location)], 
            SECONDHAND: [MessageHandler(filters.LOCATION, second_hand_location)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button))
    # application.add_handler(CallbackQueryHandler(button2))

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
