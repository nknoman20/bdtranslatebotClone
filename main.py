import os
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from googletrans import Translator
from grammar_fixer import fix_grammar

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token from environment
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set!")

# Flask and Bot setup
bot = Bot(token=TOKEN)
app = Flask(__name__)
translator = Translator(service_urls=['translate.googleapis.com'])

# Dispatcher
dispatcher = Dispatcher(bot, None, use_context=True)

# General message handler with grammar fix and translate
def handle_message(update, context):
    text = update.message.text
    lang = translator.detect(text).lang
    dest_lang = 'bn' if lang == 'en' else 'en'

    fixed_text = fix_grammar(text, lang)
    try:
        translated = translator.translate(fixed_text, dest=dest_lang).text
        translated = fix_grammar(translated, dest_lang)
        update.message.reply_text(translated)
    except Exception as e:
        update.message.reply_text("❌ Translation failed.")
        logger.error(f"Translation error: {e}")

# /translate command handler
def translate_command(update, context):
    if not context.args:
        update.message.reply_text(
            "⚠️ দয়া করে /translate এর পরে কিছু লিখুন।\nউদাহরণ: `/translate Hello`", 
            parse_mode="Markdown"
        )
        return
    text = ' '.join(context.args)
    lang = translator.detect(text).lang
    dest_lang = 'bn' if lang == 'en' else 'en'

    fixed_text = fix_grammar(text, lang)
    try:
        translated = translator.translate(fixed_text, dest=dest_lang).text
        translated = fix_grammar(translated, dest_lang)
        update.message.reply_text(f"🔁 {translated}")
    except Exception as e:
        update.message.reply_text("❌ Translation failed.")
        logger.error(f"Command translation error: {e}")

# Add handlers
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
dispatcher.add_handler(CommandHandler("translate", translate_command))

# Webhook endpoint
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# Health check route
@app.route("/", methods=["GET"])
def index():
    return "BD Translate Bot is live!", 200

# Run server
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    logger.info("Starting Flask server...")
    app.run(host="0.0.0.0", port=PORT)
