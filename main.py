import os
import logging
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, Filters
from googletrans import Translator

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tokens
TOKEN = os.getenv("BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")
if not TOKEN or not HF_TOKEN:
    raise RuntimeError("BOT_TOKEN or HF_TOKEN is missing!")

# Flask and Bot setup
app = Flask(__name__)
bot = Bot(token=TOKEN)
translator = Translator()
dispatcher = Dispatcher(bot, None, use_context=True)

# Grammar Fix Function
def fix_grammar(text, lang):
    if lang == 'bn':
        model_url = "https://api-inference.huggingface.co/models/csebuetnlp/banglat5"
    elif lang == 'en':
        model_url = "https://api-inference.huggingface.co/models/vennify/t5-base-grammar-correction"
    else:
        return text  # unsupported language

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": text}

    try:
        response = requests.post(model_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()[0]['generated_text']
    except Exception as e:
        logger.error("Grammar fix error: %s", e)
        return text

# General message handler
def handle_message(update, context):
    text = update.message.text
    lang = translator.detect(text).lang
    dest_lang = 'bn' if lang == 'en' else 'en'

    logger.info(f"Received: {text} | Lang: {lang} → {dest_lang}")

    try:
        fixed_input = fix_grammar(text, lang)
        translated = translator.translate(fixed_input, dest=dest_lang).text
        fixed_output = fix_grammar(translated, dest_lang)
        update.message.reply_text(fixed_output)
    except Exception as e:
        logger.error(f"Translation error: {e}")
        update.message.reply_text("❌ Translation failed.")

# Add message handler only (no /translate)
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Webhook endpoint
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# Status route
@app.route("/", methods=["GET"])
def index():
    return "BD Translate Bot is live!", 200

# Run server
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))
    logger.info("Starting Flask server...")
    app.run(host="0.0.0.0", port=PORT)
