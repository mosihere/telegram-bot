import os
import logging
from telegram.ext import Application

# Retrieve bot token from environment
TOKEN = os.environ.get('BOT_TOKEN')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# Set higher logging level for httpx to avoid logging all GET and POST requests
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Initialize bot application
bot = Application.builder().token(TOKEN).build()