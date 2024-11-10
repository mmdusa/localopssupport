import json
import os
import datetime
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

ADMIN_CHAT_ID = 1831118104  # Replace this with your correct Telegram ID

# Your bot token
BOT_TOKEN = '8029821604:AAEn_7GsqKiEoxo5E8_GvO5XmO-fBO8rSr0'

# Admin/Owner chat ID (your Telegram ID)
ADMIN_CHAT_ID = '1831118104'
# Define allowed user IDs


# Global dictionaries for messages and buttons based on language
LANGUAGES = {
    'en': {
        'welcome_message': "🇬🇧 Welcome \n"
                           "courier FAQ Bot,❓📚"
                           "\n"
                           " you can find Answers related to your Question.",
        'buttons': [
            {"name": "🗓️ SHIFT PLANNING", "sub_options": [
                {"name": "HOW TO ENTER MY AVAILABILITY", "description_key": "HOW_TO_ENTER_MY_AVAILABILITY"},
                {"name": "HOW DO I MOVE MY SHIFT", "description_key": "HOW_DO_I_MOVE_MY_SHIFT"}
            ]},
            {"name": "🤒 SICK LEAVE", "sub_options": [
                {"name": "WHAT TO DO IF I AM SICK?", "description_key": "WHAT_TO_DO_IF_I_AM_SICK"}
            ]},
            {"name": "🚑 INJURY", "sub_options": [
                {"name": "WHAT TO DO IF I GET INJURED?", "description_key": "WHAT_TO_DO_IF_I_GET_INJURED"},
                {"name": "INJURY CLOSURE/EXTENSION", "description_key": "INJURY_CLOSURE_EXTENSION"}
            ]},
            {"name": "💰 PAYMENT", "sub_options": [
                {"name": "WHERE CAN I CHECK MY PAY SLIP", "description_key": "WHERE_CAN_I_CHECK_MY_PAY_SLIP"}
            ]},
            {"name": "🌴 VACATION", "sub_options": [
                {"name": "HOW DO I REQUEST HOLIDAYS", "description_key": "HOW_DO_I_REQUEST_HOLIDAYS"}
            ]}
        ]
    },
    'it': {
        'welcome_message': "🇮🇹 Benvenuto,\n"
                           "corriere FAQ Bot,❓📚"
                           "\n"
                           " puoi trovare le risposte relative alla tua domanda.",
        'buttons': [
            {"name": "🗓️ TURNI DI LAVORO", "sub_options": [
                {"name": "COME INSERIRE LE DISPONIBILITÀ", "description_key": "COME_INSERIRE_LE_DISPONIBILITA_IT"},
                {"name": "COME FACCIO A SPOSTARE UN TURNO", "description_key": "COME_FACCIO_A_SPOSTARE_UN_TURNO_IT"}
            ]},
            {"name": "🤒 MALATTIA", "sub_options": [
                {"name": "COSA FARE IN CASO DI MALATTIA?", "description_key": "COSA_FARE_IN_CASO_DI_MALATTIA_IT"}
            ]},
            {"name": "🚑 INFORTUNIO", "sub_options": [
                {"name": "COSA FARE IN CASO DI INFORTUNIO?", "description_key": "COSA_FARE_IN_CASO_DI_INFORTUNIO_IT"},
                {"name": "CHIUSURA/ESTENSIONE DELL'INFORTUNIO", "description_key": "CHIUSURA_ESTENSIONE_INFORTUNIO_IT"}
            ]},
            {"name": "💰 PAGAMENTO", "sub_options": [
                {"name": "DOVE POSSO CONTROLLARE LA MIA BUSTA PAGA", "description_key": "DOVE_POSSO_CONTROLARE_LA_MIA_BUSTA_PAGA_IT"}
            ]},
            {"name": "🌴 VACANZE", "sub_options": [
                {"name": "COME RICHIEDERE LE FERIE", "description_key": "COME_RICHIEDERE_LE_FERIE_IT"}
            ]}
        ]
    }
}

from telegram import InputFile
import pandas as pd
import datetime
import os


import pandas as pd
import datetime
import os
import gspread
import time
import schedule
import threading
from oauth2client.service_account import ServiceAccountCredentials

ADMIN_CHAT_ID = 1831118104  # Replace this with your correct Telegram ID


ALLOWED_USER_IDS = [1831118104, 7221136452, 6994346288, 1774111011,1875631123, 5387976775, 1420246203, 5031258957, 1760090359, 312399260]

# Function to check if a user is allowed to access the bot
def is_user_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USER_IDS

# File to store approved user IDs
ALLOWED_USERS_FILE = "allowed_users.json"

# Load allowed users from the JSON file
def load_allowed_users():
    try:
        with open(ALLOWED_USERS_FILE, "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

# Function to save allowed users to the JSON file
def save_allowed_users():
    with open(ALLOWED_USERS_FILE, "w") as f:
        json.dump(list(ALLOWED_USER_IDS), f, indent=4)

# Initialize allowed users
ALLOWED_USER_IDS = set(load_allowed_users())

# Google Sheets setup
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Use your downloaded service account key file
creds = ServiceAccountCredentials.from_json_keyfile_name("C:\\Users\\asus\\Desktop\\Bot\\feedback.json", scope)
client = gspread.authorize(creds)

descriptions_sheet = client.open("Descriptions_Sheet").sheet1  # Replace with actual sheet name
descriptions_cache = {}

# Now you should be able to access your sheet
sheet = client.open("feedback_bot").sheet1
# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    user_id, first_name, last_name = user.id, user.first_name or "User", user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()

    if not is_user_allowed(user_id):
        keyboard = [[InlineKeyboardButton("Request Access", callback_data="request_access")]]
        await update.message.reply_text(
            "🚫 You are not allowed to use this bot. Please request access.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"User started the bot:\nID: {user_id}\nName: {first_name} {last_name}"
    )

    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')],
        [InlineKeyboardButton("🇮🇹 Italiano", callback_data='lang_it')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Hello {first_name} {last_name},\n\n"
        "🇬🇧 We kindly ask you to choose your preferred language.\n\n"
        "🇮🇹 Ti chiediamo gentilmente di scegliere la lingua che preferisci:",
        reply_markup=reply_markup
    )


descriptions_cache = {}

def load_descriptions():
    """Load all descriptions from Google Sheets into the cache."""
    global descriptions_cache
    descriptions_cache = {row[0]: row[1] for row in descriptions_sheet.get_all_values()}
    print("Descriptions cache updated from Google Sheets")

# Initial load of descriptions at startup
load_descriptions()

# Function to get the description from the cache
def get_description(description_key):
    return descriptions_cache.get(description_key, "Description not available")

# Schedule a refresh of the descriptions cache every minute
schedule.every(1).minutes.do(load_descriptions)

# Run the scheduler in a separate thread
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()

# Example usage
#description = get_description("HOW_TO_ENTER_MY_AVAILABILITY")
#print(description)  # This will print the latest description from the cache


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str) -> None:
    user_id = update.effective_user.id
    if not is_user_allowed(user_id):
        if update.message:
            await update.message.reply_text("🚫 You are not allowed to use this bot.")
        elif update.callback_query:
            await update.callback_query.message.reply_text("🚫 You are not allowed to use this bot.")
        return
    keyboard = [[InlineKeyboardButton(option['name'], callback_data=f"option_{language}_{i}")]
                for i, option in enumerate(LANGUAGES[language]['buttons'])]
    keyboard.append([InlineKeyboardButton("📝 Feedback", callback_data="feedback")])
    keyboard.append([InlineKeyboardButton("🌐 Useful Websites", callback_data="show_websites")])

    if language == 'en':
        keyboard.append([InlineKeyboardButton("🇮🇹 Versione italiana", callback_data='lang_it')])
    else:
        keyboard.append([InlineKeyboardButton("🇬🇧 English Version", callback_data='lang_en')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.message.edit_text(LANGUAGES[language]['welcome_message'], reply_markup=reply_markup)
    else:
        if update.message:
            await update.message.reply_text(LANGUAGES[language]['welcome_message'], reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.message.edit_text(LANGUAGES[language]['welcome_message'],
                                                          reply_markup=reply_markup)


## FOR ACCESS AND REJECT PLACE THE CODE HERE.


# Function to handle feedback messages, photos, and videos
async def handle_feedback_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if not is_user_allowed(user_id):
        await update.message.reply_text("🚫 You are not allowed to use this bot.")
        return

# Create a directory for saving media files if it doesn't exist
MEDIA_DIRECTORY = "media_files"
if not os.path.exists(MEDIA_DIRECTORY):
    os.makedirs(MEDIA_DIRECTORY)

# Function to handle text feedback and media files
async def handle_feedback_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    user_id = user.id
    first_name = user.first_name if user.first_name else "No first name"
    last_name = user.last_name if user.last_name else "No last name"
    username = user.username if user.username else "No username"
    phone_number = update.message.contact.phone_number if update.message.contact else "No phone number"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if update.message.text:
        if context.user_data.get("awaiting_feedback"):
            feedback = update.message.text
            sheet.append_row([timestamp, user_id, first_name, last_name, username, phone_number, feedback, "Text", "N/A"])
            context.user_data["awaiting_feedback"] = False
        else:
            await update.message.reply_text(
                "Sorry, I don't understand your message. "
                "Use one of the options."
                "\n\n Mi dispiace, non capisco il tuo messaggio. Usa una delle opzioni."
            )
            return

    elif update.message.photo:
        if context.user_data.get("awaiting_feedback"):
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            file_path = f"{MEDIA_DIRECTORY}/photo_{user_id}_{photo.file_id}.jpg"
            await file.download_to_drive(file_path)

            sheet.append_row([timestamp, user_id, first_name, last_name, username, phone_number, "Photo sent", "Photo", file_path])
            context.user_data["awaiting_feedback"] = False
        else:
            await update.message.reply_text(
                "Sorry, I don't understand your message. "
                "Use one of the options."
                "\n\n Mi dispiace, non capisco il tuo messaggio. Usa una delle opzioni."
            )
            return

    elif update.message.video:
        if context.user_data.get("awaiting_feedback"):
            video = update.message.video
            file = await context.bot.get_file(video.file_id)
            file_path = f"{MEDIA_DIRECTORY}/video_{user_id}_{video.file_id}.mp4"
            await file.download_to_drive(file_path)

            sheet.append_row([timestamp, user_id, first_name, last_name, username, phone_number, "Video sent", "Video", file_path])
            context.user_data["awaiting_feedback"] = False
        else:
            await update.message.reply_text(
                "Sorry, I don't understand your message. "
                "Use one of the options."
                "\n\n Mi dispiace, non capisco il tuo messaggio. Usa una delle opzioni."
            )
            return

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Feedback from {first_name} {last_name} (ID: {user_id}) recorded.")
    await update.message.reply_text("Thank you for your feedback! 🙏"
                                    "\n grazie per il tuo feedback 🙏")
    language = 'en'
    await show_main_menu(update, context, language)

# Set 'awaiting_feedback' to True when the feedback button is selected
async def handle_feedback_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["awaiting_feedback"] = True
    await update.callback_query.message.reply_text("Please type your feedback or send a photo/video, and I will log it.")


# Function to show the website buttons
async def show_websites(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("HR ZUCCHETTI",
                              url="https://saas.hrzucchetti.it/hrpzs12/jsp/login.jsp?cpccchk=0.844827148043025")],
        [InlineKeyboardButton("WEB SHOP", url="https://scooberwebshop.takeaway.com/login")],
        [InlineKeyboardButton("VEHICLE CHECK",
                              url="https://docs.google.com/forms/d/e/1FAIpQLScpaK_HVvZ-iBAszxllo12UFySy_iVs2_Ud2DYLSLWq5U6Z2Q/viewform")],
        [InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_main_en")],  # Add back to main menu button
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.edit_text("Here are some useful websites:"
                                                  "\n"
                                                  "Ecco alcuni siti web utili:", reply_markup=reply_markup)


# Callback query handler for language selection and main menu display
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = query.from_user
    user_id = user.id
    first_name = user.first_name if user.first_name else "No first name"
    last_name = user.last_name if user.last_name else "No last name"
    username = user.username if user.username else "No username"
    phone_number = user.phone_number if hasattr(user, 'phone_number') else "No phone number"

    query_data = query.data
    if query_data == "request_access":
        # Send immediate confirmation to the user that the request has been received
        await query.answer("We have received your request. It will be reviewed shortly.", show_alert=True)
        await query.message.edit_text("Your access request has been sent to the admin. Please wait for approval.")

        # Notify admin
        admin_message = (
            f"🚨 Access request received from user {user_id}!\n"
            f"Name: {first_name} {last_name}\n"
            f"Username: @{username}\n"
            f"Phone: {phone_number}\n"
            f"User ID: {user_id}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)

        # Show Approve/Deny buttons for admin
        admin_controls = [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton("❌ Deny", callback_data=f"deny_{user_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(admin_controls)
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text="Approve or deny access request:", reply_markup=reply_markup)

    elif user_id not in ALLOWED_USER_IDS:
        # If the user is not allowed, remove the buttons and inform them about restricted access
        await query.answer("Access restricted. Please request access from the admin.", show_alert=True)
        await query.message.edit_text(
            "You do not have permission to use this bot. Please request access from the admin.", reply_markup=None)

    elif query_data.startswith("approve_"):
        requested_user_id = int(query_data.split('_')[1])
        if requested_user_id not in ALLOWED_USER_IDS:
            ALLOWED_USER_IDS.add(requested_user_id)
            save_allowed_users()  # Save the updated list
            await context.bot.send_message(chat_id=requested_user_id, text="🎉 You have been approved to use the bot use /start to run the bot!")
            await query.message.reply_text("User has been approved successfully.")

        else:
            await query.message.reply_text("User is already approved.")

        # Remove the inline keyboard
        await query.edit_message_reply_markup(reply_markup=None)

    elif query_data.startswith("deny_"):
        requested_user_id = int(query_data.split('_')[1])
        await context.bot.send_message(chat_id=requested_user_id, text="🚫 Your access request has been denied.")
        await query.message.reply_text("User access request has been denied.")

        # Remove the inline keyboard
        await query.edit_message_reply_markup(reply_markup=None)

    # Language selection
    elif query_data.startswith('lang_'):
        language = query_data.split('_')[1]
        await show_main_menu(update, context, language)

    # Feedback handling
    elif query_data == "feedback":
        await query.message.reply_text(
            "📝We're happy to receive your feedback! Please write your feedback in the text box!"
            "\n"
            "\n"
            "📝Siamo felici di ricevere il tuo feedback! Scrivi il tuo feedback"
        )
        # Set the context to expect feedback
        context.user_data['awaiting_feedback'] = True

    # Handle website button click
    elif query_data == "show_websites":
        await show_websites(update, context)

    # Main menu options (e.g., SHIFT PLANNING, SICK LEAVE)
    elif query_data.startswith('option_'):
        _, language, option_index = query_data.split('_', 2)
        option_index = int(option_index)
        option = LANGUAGES[language]['buttons'][option_index]

        # Create sub-options keyboard (second level of options)
        keyboard = [[InlineKeyboardButton(sub_option['name'], callback_data=f"suboption_{language}_{option_index}_{i}")]
                    for i, sub_option in enumerate(option['sub_options'])]

        # Add only the "Back to Main Menu" button here
        keyboard.append([InlineKeyboardButton("🏠 Back to Main Menu", callback_data=f"back_main_{language}")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text(f"Selected: {option['name']}", reply_markup=reply_markup)

    # Sub-option handling
    elif query_data.startswith('suboption_'):
        _, language, option_index, sub_option_index = query_data.split('_')
        option_index, sub_option_index = int(option_index), int(sub_option_index)
        description_key = LANGUAGES[language]['buttons'][option_index]['sub_options'][sub_option_index][
            'description_key']

        # Fetch the description dynamically
        description = get_description(description_key)

        # In the last level (description level), show both "Back to Previous Menu" and "Back to Main Menu" buttons
        keyboard = [
            [InlineKeyboardButton(
                "⬅️ Back to Previous Menu" if language == 'en' else "⬅️ Torna al menu precedente",
                callback_data=f"back_option_{language}_{option_index}"
            )],
            [InlineKeyboardButton(
                "🏠 Back to Main Menu" if language == 'en' else "🏠 Torna al menu principale",
                callback_data=f"back_main_{language}"
            )]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text(description, reply_markup=reply_markup)

    # Handle returning to the previous menu (list of sub-options)
    elif query_data.startswith('back_option_'):
        parts = query_data.split('_')
        language = parts[2]
        option_index = int(parts[3])

        option = LANGUAGES[language]['buttons'][option_index]

        keyboard = [[InlineKeyboardButton(sub_option['name'], callback_data=f"suboption_{language}_{option_index}_{i}")]
                    for i, sub_option in enumerate(option['sub_options'])]
        keyboard.append([InlineKeyboardButton(
            "🏠 Back to Main Menu" if language == 'en' else "🏠 Torna al menu principale",
            callback_data=f"back_main_{language}"
        )])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text(f"Selected: {option['name']}", reply_markup=reply_markup)

    # Return to the main menu
    elif query_data.startswith('back_main_'):
        language = query_data.split('_')[2]
        await show_main_menu(update, context, language)

async def request_access_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    await update.message.reply_text("Your request has been sent to the admin for approval.")
    await button_click(update, context)

# Main function to run the bot
def main() -> None:
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler("request_access", request_access_command))
    #application.add_handler(CommandHandler('approve', approve))
    #application.add_handler(CommandHandler('reject', reject))

    application.add_handler(CallbackQueryHandler(button_click))
    # Handle user feedback (now handles text, photos, and videos)
    # MessageHandler for feedback, ignoring commands
    application.add_handler(
        MessageHandler((filters.TEXT | filters.PHOTO | filters.VIDEO) & ~filters.COMMAND, handle_feedback_message))

    # Start the bot
    application.run_polling()


if __name__ == '__main__':
    main()
