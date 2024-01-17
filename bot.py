from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

# Google OAuth Configuration
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
CLIENT_SECRETS_FILE = 'client_secrets.json'

# Telegram Bot Token
TOKEN = 'token'

# Helper function to get the YouTube service
def get_youtube_service(credentials):
    return build('youtube', 'v3', credentials=credentials)

# Command handlers
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hello! Welcome to your YouTube bot. Use /login to authenticate.")



def login(update: Update, context: CallbackContext) -> None:
    # Create OAuth flow with explicit redirect_uri
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')#urn:ietf:wg:oauth:2.0:oob  redirect_uri='https://oauth.pstmn.io/v1/callback',)
    
    # Generate authentication URL
    auth_url, _ = flow.authorization_url()

    # Create a button with the authentication link
    keyboard = [[InlineKeyboardButton("Authenticate", url=auth_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the authentication link to the user as a button
    update.message.reply_text("Click the button to authenticate:", reply_markup=reply_markup)

def callback_handler(update: Update, context: CallbackContext) -> None:
    # Retrieve OAuth flow from user's context
    flow = context.user_data['oauth_flow']
    
    # Get authorization response from the callback link
    authorization_response = update.message.text
    
    try:
        # Exchange the authorization response for credentials
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials

        # Store the credentials in the user's context for later use
        context.user_data['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

        # Use the credentials to access YouTube API or store for later use
        youtube_service = get_youtube_service(credentials)

        # Do something with the YouTube service, like fetching comments

        # Clear the stored flow from user's context
        del context.user_data['oauth_flow']

        update.message.reply_text("Authentication successful! You can now use other bot features.")
    except Exception as e:
        update.message.reply_text(f"Error during authentication: {str(e)}")
        # Handle the error as needed

# Set up the Telegram bot
updater = Updater(TOKEN)
dispatcher = updater.dispatcher

# Add command handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("login", login))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, callback_handler))

# Start the bot
updater.start_polling()
updater.idle()
