from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from pyrogram.errors import BadRequest, exceptions
import config
import mysqlm as db
import tempmail
import logging

# creating client
app = Client(
    "Fakemaiil",
    api_id=config.api_id, api_hash=config.api_hash,
    bot_token=6067177575:AAEip8P4fVsQDEpG_LiNRTyqKFiPgy04qvs
)


# creating filter for check if user is in the channels
async def join(flt: Client, bot: Client, query: Message):
    user_id = query.from_user.id
    try:
        for channel in channels_buttons[0]:
            channel_url = '@' + channel.url.split('https://t.me/')[1]
            await bot.get_chat_member(
                chat_id=channel_url, user_id=user_id)
        return True

    # this except is for users that not joined the channels
    except exceptions.bad_request_400.UserNotParticipant:
        user_name = query.chat.first_name
        await bot.send_message(
            chat_id=user_id,
            text=f"""
            سلام {user_name} خوش اومدی 🌹
            برای استفاده از ربات باید عضو کانال  ها زیر بشی""",
            reply_markup=markup_channels)
        return False

    # this except is for admin that shows channels not found by bot
    except BadRequest:
        await bot.send_message(
            chat_id=config.admin_id,
            text=f"یکی از کانال ها برای بررسی کاربر پیدا نشد",
            reply_markup=markup_channels)


# crating filter
is_join = filters.create(join)


# start command
@app.on_message(filters.command('start') & filters.private)
async def start(bot: Client, message: Message):
    user_name = message.chat.first_name
    user_username = message.chat.username
    chat_id = message.chat.id
    text = f"""
سلام {user_name} خوش اومدی 🌹

➕ با من به راحتی به از فضای مجازی استفاده کن

🔸 برای شروع با کمک گرفتن از دکمه های پایینی ایمیل خودت رو بساز :
"""
    await bot.send_message(chat_id, text, reply_markup=markup_buttons)
    db.add_user(chat_id, user_name, user_username)


# users command for admin
# this command shows the count of all users
@app.on_message(filters.command('users') & filters.user(config.admin_id))
async def users(bot: Client, message: Message):
    result = db.all_users()
    await message.reply_text(result)


# this command handel text messages
@app.on_message(filters.text & is_join)
async def messages(bot: Client, message: Message):

    chat_id = message.chat.id
    msg_txt = message.text

    # if message is create password
    if msg_txt == '📥 ایجاد ایمیل':
        email = tempmail.generate()
        db.add_email(email, chat_id)
        await message.reply_text(text=f"__**ایمیل شما**__ : `{email}`",
                                 parse_mode=enums.ParseMode.MARKDOWN)

    # elif message is refresh
    elif msg_txt == '🔄 بروزرسانی':
        try:

            email = db.read_email(chat_id)[0]
            username, domain = email.split("@")
            # Get incoming email
            email_id, email_from, email_subject, email_date, email_text, files = tempmail.refresh(
                username, domain)

            files_text = "\n".join(files) if files else ""
            text = f"""
➖➖➖➖➖➖➖➖➖
From: <{email_from}>
To: <{email}>
Date: {email_date}
Attachments: {files_text}
➖➖➖➖➖➖➖➖➖
Subject: {email_subject}
➖➖➖➖➖➖➖➖➖
{email_text}
"""
            await bot.send_message(chat_id, text, disable_web_page_preview=True)

        # if there is no incoming email
        except ValueError:
            await message.reply_text(text="هنوز ایمیلی دریافت نشده است.",
                                     parse_mode=enums.ParseMode.MARKDOWN)

    # elif message is my email
    elif msg_txt == '📬 ایمیل من':
        email = db.read_email(chat_id)[0]
        await message.reply_text(text=f"__**ایمیل شما**__ : `{email}`",
                                 parse_mode=enums.ParseMode.MARKDOWN)

    # if message is somthing else
    else:
        await message.reply_text(text=f"متوجه نشدم!",
                                 parse_mode=enums.ParseMode.MARKDOWN)


if __name__ == '__main__':
    try:
        # for logging errors
        logging.basicConfig(filename='errors.log', level=logging.ERROR,
                            format='%(asctime)s %(levelname)s: %(message)s')

        # this is our KeyboardButtons
        markup_buttons = ReplyKeyboardMarkup([
            [KeyboardButton('📥 ایجاد ایمیل')],  # creating email button
            [KeyboardButton('🔄 بروزرسانی'),  # refresh email for new emails button
             KeyboardButton('📬 ایمیل من')],  # show current email button
        ], resize_keyboard=True)

        # this is our channel that user must to join
        channels_buttons = [
            [InlineKeyboardButton('AlihtBots', url='https://t.me/AlihtBots'),
             InlineKeyboardButton('IplaymeI', url='https://t.me/IplaymeI')], ]

        # This is the submit button for after the user joins the channel
        channels_submit_button = [[InlineKeyboardButton(
            'جوین شدم ✅', url='https://t.me/FakemaiilRobot?start=start')]]

        # this is buttons markup for channels
        markup_channels = InlineKeyboardMarkup(
            channels_buttons + channels_submit_button)

        print('bot is alive')
        app.run()

    # logging all errors
    except Exception as e:
        logging.error(str(e))
