import logging
import os
import random
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
import google.generativeai as genai

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(name)

# Gemini sozlash
api_key= "AQ.Ab8RN6IQ3RQwI1rct5vI17KnM8NfObi3yoBOes46j3yrizkCGw"
model = genai.GenerativeModel("gemini-1.5-flash")

# States
MAIN_MENU, WRITING_WAIT, SPEAKING_WAIT, READING_WAIT = range(4)

# ===================== KLAVIATURALAR =====================

def main_keyboard():
    buttons = [
        [KeyboardButton("✍️ Writing tekshirish")],
        [KeyboardButton("🗣 Speaking savollari")],
        [KeyboardButton("📖 Reading mashqlar")],
        [KeyboardButton("🎧 Listening mashqlar")],
        [KeyboardButton("ℹ️ Yordam")],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def back_keyboard():
    return ReplyKeyboardMarkup([[KeyboardButton("🔙 Orqaga")]], resize_keyboard=True)

# ===================== SPEAKING SAVOLLARI =====================

SPEAKING_QUESTIONS = [
    "Describe your hometown. What do you like most about it?",
    "Talk about a book or movie that influenced you. Why was it important?",
    "Describe a person you admire. What qualities do they have?",
    "Talk about your favorite hobby. How did you start it?",
    "Describe a memorable trip you took. What made it special?",
    "Talk about a challenge you faced and how you overcame it.",
    "Describe your ideal job. What skills would you need?",
    "Talk about the importance of learning English in your country.",
    "Describe a traditional food from your culture.",
    "Talk about technology's impact on education.",
]

LISTENING_TOPICS = [
    "🎧 Listening Mashq 1 - Academic\n\nQuyidagi savolga javob yozing:\n\nA university lecture about climate change is being discussed. The professor mentions THREE main causes. Listen and write them down.\n\n💡 *Amaliyot uchun:* BBC Learning English yoki IELTS.org saytidan audio topib, shu mavzuda mashq qiling.",
    "🎧 Listening Mashq 2 - General\n\nTelephone conversation:\nA customer is calling a hotel to make a reservation.\n\n❓ Savollar:\n1. What type of room does the customer want?\n2. How many nights will they stay?\n3. What is the check-in date?\n\n💡 *Amaliyot uchun:* IELTS Cambridge kitoblaridan listening topshiriqlarini bajaring.",
    "🎧 Listening Mashq 3 - Map/Diagram\n\nA tour guide is explaining a museum layout.\n\n❓ Savollar:\n1. Where is the gift shop located?\n2. Which floor has the modern art section?\n3. What is near the main entrance?\n\n💡 *Amaliyot uchun:* IELTS Liz yoki IELTS Simon YouTube kanallarini ko'ring.",
]

READING_PASSAGES = [
    {
        "title": "The Impact of Social Media on Society",
        "text": """Social media has fundamentally transformed the way people communicate and share information. Platforms like Facebook, Instagram, and Twitter have created new forms of social interaction that transcend geographical boundaries. While these platforms offer unprecedented connectivity, they also present significant challenges.

Research suggests that excessive social media use can lead to feelings of anxiety and depression, particularly among young people. The constant exposure to curated versions of others' lives can create unrealistic expectations and feelings of inadequacy. Furthermore, the spread of misinformation has become a major concern, with false information spreading rapidly across networks.

On the positive side, social media has democratized information sharing, giving voice to marginalized communities and enabling rapid coordination during emergencies. It has also revolutionized business marketing and created new economic opportunities.""",
      "questions": [
            "1. According to the passage, what is ONE negative effect of social media on young people?",
            "2. What does 'democratized information sharing' mean in the context of the passage?",
            "3. TRUE/FALSE/NOT GIVEN: Social media has completely eliminated geographical barriers in communication.",
        ]
    },
    {
        "title": "Renewable Energy: The Future of Power",
        "text": """The global transition to renewable energy sources represents one of the most significant shifts in human history. Solar and wind power have seen dramatic cost reductions over the past decade, making them increasingly competitive with fossil fuels. In many regions, renewable energy is now the cheapest source of new electricity generation.

However, the transition faces several challenges. Energy storage remains a critical issue, as solar and wind power are intermittent sources. Battery technology has improved significantly, but storing large amounts of energy for extended periods remains expensive. Grid infrastructure also needs substantial upgrades to handle distributed energy sources.

Despite these challenges, the momentum behind renewable energy is unstoppable. Government policies, corporate commitments, and falling technology costs are driving rapid deployment worldwide.""",
        "questions": [
            "1. What TWO challenges does the passage mention for renewable energy transition?",
            "2. Why are solar and wind power described as 'intermittent sources'?",
            "3. TRUE/FALSE/NOT GIVEN: Battery technology has not improved in recent years.",
        ]
    }
]

# ===================== HANDLERLAR =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Assalomu alaykum, {user.first_name}! 👋\n\n"
        "🎓 *IELTS Tayyorgarlik Botiga Xush Kelibsiz!*\n\n"
        "Bu bot sizga IELTS imtihoniga tayyorlanishda yordam beradi:\n\n"
        "✍️ *Writing* — Esseyingizni tekshirish va band score\n"
        "🗣 *Speaking* — Amaliyot savollari\n"
        "📖 *Reading* — Matn va savollar\n"
        "🎧 *Listening* — Mashq topshiriqlari\n\n"
        "Quyidagi menyudan tanlang 👇",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )
    return MAIN_MENU

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "✍️ Writing tekshirish":
        await update.message.reply_text(
            "✍️ *Writing Tekshirish*\n\n"
            "Esseyingizni yuboring, men:\n"
            "• Band Score (0-9) beraman\n"
            "• Task Achievement tekshiraman\n"
            "• Coherence & Cohesion baholayman\n"
            "• Vocabulary va Grammar tekshiraman\n"
            "• Tavsiyalar beraman\n\n"
            "📝 *Esseyingizni shu yerga yozing:*",
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )
        return WRITING_WAIT

    elif text == "🗣 Speaking savollari":
        question = random.choice(SPEAKING_QUESTIONS)
        await update.message.reply_text(
            f"🗣 *Speaking Savoli:*\n\n"
            f"❓ _{question}_\n\n"
            f"💡 *Tavsiya:* 1-2 daqiqa davomida javob bering.\n"
            f"Javobingizni matn ko'rinishida yuboring — men tekshirib beraman!",
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )
        context.user_data["mode"] = "speaking"
        return SPEAKING_WAIT

    elif text == "📖 Reading mashqlar":
        passage = random.choice(READING_PASSAGES)
        questions_text = "\n".join(passage["questions"])
        await update.message.reply_text(
            f"📖 *Reading Mashq*\n\n"
      f"{passage['title']}\n\n"
            f"{passage['text']}\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"❓ *Savollarga javob bering:*\n\n"
            f"{questions_text}\n\n"
            f"📝 Javoblaringizni yuboring:",
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )
        context.user_data["mode"] = "reading"
        context.user_data["passage"] = passage
        return READING_WAIT

    elif text == "🎧 Listening mashqlar":
        topic = random.choice(LISTENING_TOPICS)
        await update.message.reply_text(
            topic,
            parse_mode="Markdown",
            reply_markup=main_keyboard()
        )
        return MAIN_MENU

    elif text == "ℹ️ Yordam":
        await update.message.reply_text(
            "ℹ️ *Yordam*\n\n"
            "🤖 Bu bot Gemini AI yordamida ishlaydi.\n\n"
            "📌 *Qanday foydalanish:*\n"
            "1. *Writing* — Esseyingizni to'liq yuboring\n"
            "2. *Speaking* — Savolga matn javob yuboring\n"
            "3. *Reading* — Matnni o'qib savollarga javob bering\n"
            "4. *Listening* — Topshiriqni bajaring\n\n"
            "📊 *Band Score tizimi:*\n"
            "9 — Expert\n8 — Very Good\n7 — Good\n"
            "6 — Competent\n5 — Modest\n\n"
            "💬 Savollar uchun: @admin",
            parse_mode="Markdown",
            reply_markup=main_keyboard()
        )
        return MAIN_MENU

    return MAIN_MENU

async def writing_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Orqaga":
        await update.message.reply_text("Asosiy menyu 👇", reply_markup=main_keyboard())
        return MAIN_MENU

    await update.message.reply_text("⏳ Esseyingiz tekshirilmoqda... bir oz kuting.")

    prompt = f"""Sen IELTS Writing examinersan. Quyidagi esseyni IELTS kriteriyalari bo'yicha baholab ber.

ESSAY:
{text}

Quyidagi formatda O'ZBEK tilida javob ber:

📊 UMUMIY BAND SCORE: [0-9]

📋 KRITERIYALAR BO'YICHA BAHOLASH:
• Task Achievement/Response: [band] — [qisqa izoh]
• Coherence & Cohesion: [band] — [qisqa izoh]
• Lexical Resource: [band] — [qisqa izoh]
• Grammatical Range & Accuracy: [band] — [qisqa izoh]

✅ KUCHLI TOMONLAR:
[2-3 ta ijobiy jihat]

❌ KAMCHILIKLAR:
[2-3 ta asosiy kamchilik]

💡 TAVSIYALAR:
[Yaxshilash uchun 3 ta aniq tavsiya]

📝 MISOL TUZATISHLAR:
[1-2 ta jumlani tuzatib ko'rsat]"""

    try:
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text, reply_markup=back_keyboard())
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        await update.message.reply_text(
            "❌ Xatolik yuz berdi. Iltimos qayta urinib ko'ring.",
            reply_markup=back_keyboard()
        )
    return WRITING_WAIT

async def speaking_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Orqaga":
        await update.message.reply_text("Asosiy menyu 👇", reply_markup=main_keyboard())
        return MAIN_MENU

    await update.message.reply_text("⏳ Javobingiz tahlil qilinmoqda...")

    prompt = f"""Sen IELTS Speaking examinersan. Quyidagi speaking javobini baholab ber.

JAVOB:
{text}

O'ZBEK tilida quyidagi formatda:

🎯 UMUMIY BAND SCORE: [0-9]

📋 BAHOLASH:
• Fluency & Coherence: [band] — [izoh]
• Lexical Resource: [band] — [izoh]
• Grammatical Range: [band] — [izoh]
• Pronunciation: [band] — [izoh]

✅ YAXSHI TOMONLAR:
[2 ta ijobiy]

💡 YAXSHILASH UCHUN:
[3 ta tavsiya]

📝 QO'SHIMCHA IBORALAR:
[Javobni boyitish uchun 3-4 ta foydali ibora]"""

    try:
        response = model.generate_content(prompt)
        new_question = random.choice(SPEAKING_QUESTIONS)
        full_response = (
            response.text +
            f"\n\n━━━━━━━━━━━━━━━\n"
      f"🔄 *Keyingi savol:*\n\n❓ _{new_question}_"
        )
        await update.message.reply_text(full_response, parse_mode="Markdown", reply_markup=back_keyboard())
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi.", reply_markup=back_keyboard())
    return SPEAKING_WAIT

async def reading_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Orqaga":
        await update.message.reply_text("Asosiy menyu 👇", reply_markup=main_keyboard())
        return MAIN_MENU

    passage = context.user_data.get("passage", {})
    await update.message.reply_text("⏳ Javoblaringiz tekshirilmoqda...")

    prompt = f"""Sen IELTS Reading o'qituvchisan.

MATN: {passage.get('title', '')}
{passage.get('text', '')}

O'QUVCHI JAVOBLARI:
{text}

O'ZBEK tilida tekshir:

✅ TO'G'RI JAVOBLAR:
[Har bir savol uchun to'g'ri javob]

📊 NATIJA: [X/3 ball]

💡 TUSHUNTIRISH:
[Har bir javobni qisqacha tushuntir]

📌 READING MASLAHATLARI:
[2-3 ta IELTS Reading strategiyasi]"""

    try:
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text, reply_markup=main_keyboard())
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi.", reply_markup=main_keyboard())
    return MAIN_MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Asosiy menyu 👇", reply_markup=main_keyboard())
    return MAIN_MENU

# ===================== MAIN =====================

def main():
    token = "8829111801:AAHSdemxCPRk9iN3i9rpvwfeq5OBZ-BpG9k"
    app = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler)],
            WRITING_WAIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, writing_handler)],
            SPEAKING_WAIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, speaking_handler)],
            READING_WAIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, reading_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    logger.info("Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if name == "main":
    main()
