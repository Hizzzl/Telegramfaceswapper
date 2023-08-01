import os
import random

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import sqlite3
import membership
import requests

import roop.ui

# Replace with your API token
API_TOKEN = '6652643521:AAHDgfx_MVs8UDsbZULuVeWTCH8al2yF0Jc'

# Initialize the bot
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Initialize database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()


@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):

    is_member = await membership.check((message.chat.id))
    if is_member:
        await sendStartMessages(message.chat.id)
        return

    if 'ref' in message.text:

        ref_code = message.text.split(' ')[1]
        balance = 0

        for i in cursor.execute("SELECT * FROM users WHERE ref=?", (ref_code,)):
            balance = i[1]

        cursor.execute("UPDATE users SET balance = ? WHERE ref = ?", (balance + 0.5, ref_code))
        conn.commit()


    keyboard = types.InlineKeyboardMarkup(row_width=2)

    channel_url = "https://t.me/facedeepapp"  # Change on your channel link
    channel_button = types.InlineKeyboardButton("Subscribe now", url=channel_url)

    button2 = types.InlineKeyboardButton("I subscribed! ✅", callback_data="show_table")

    keyboard.add(channel_button, button2)

    await bot.send_message(message.from_user.id, "To continue you need to subscribe our channel using 'subscribe now' and click 'I subscribed'!", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'show_table')
async def process_show_table(callback_query: types.CallbackQuery):
    is_member = await membership.check(callback_query.message.chat.id)

    if is_member:
        await sendStartMessages(callback_query.message.chat.id)
    else:
        await bot.answer_callback_query(callback_query.id, "You are not subscribed")


async def sendStartMessages(chat_id):
    # add user to database and give 2 free coins
    cursor.execute("SELECT * FROM users WHERE id=?", (chat_id,))
    user = cursor.fetchone()

    if user is None:

        rnd = "abcdefghijklmnpqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        ref = 'ref'
        for i in range(10):
            ref = ref + random.choice(rnd)

        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (chat_id, 2, ref))
        conn.commit()

    await bot.send_message(chat_id, """Welcome to Facedeep 🤩 The new cutting-edge Ai technology to swap faces, if it's your first time enjoy free 2 generations.  to gain more coins you can /deposit or you can earn more free coins simply just by /invite.
Payments are secure by stripe/crypto.""")


    photo = 'demo.jpg'
    with open(photo, 'rb') as photo:
        await bot.send_photo(chat_id=chat_id, photo=photo)

    await bot.send_message(chat_id, "Please send the base photo 🖼️ (Remember, this is the face you want to use)")

@dp.message_handler(commands=['balance'])
async def sendUserBalance(message: types.Message):
    if await membership.check(message.from_user.id):
        # get balance from database
        user_id = message.from_user.id
        balance = 0
        for i in cursor.execute("SELECT * FROM users WHERE id=?", (user_id,)):
            balance = i[1]

        await bot.send_message(user_id, "Your current balance - " + str(balance) + "$")

@dp.message_handler(commands=['invite'])
async def inviteInfo(message: types.Message):
    custom_link = 'https://t.me/facedeepbot?start='
    ref = ''
    user_id = message.chat.id
    for i in cursor.execute("SELECT * FROM users WHERE id=?", (user_id,)):
        ref = i[2]
    custom_link = custom_link + ref

    await bot.send_message(message.chat.id, """For every referral, you will get 0.5$ in coins balance.
Tips: 
-Share in telegram groups comments
-add a referral link to your profile
-Share generated video on (Reddit, telegram, and Discord) with a referral link""")
    await bot.send_message(message.chat.id, "This is you referral link - " + custom_link)


@dp.message_handler(commands=['faq'])
async def faqInfo(message: types.Message):
    await bot.send_message(message.chat.id, """For best results for your video/photo use this: tips:
✅ Photos with only one face looking at the camera
✅ Photos with good lighting
✅ High-quality photos
❌ Avoid full-body photos
❌ Avoid sunglasses or glasses
❌ Avoid faces covered by hair or caps
❌ Avoid multiple faces in the same photo For best results for your video
""")
    await bot.send_message(message.chat.id, """Your account is billed based on the media type (photo or video)
🎥 For videos, your account will be billed based on the processing time in minutes. Most of the time, 1 minute of video duration equals 1 minute of processing time.
If the processing time is less than a minute, you will NOT be billed for the full minute.
    
""")

@dp.message_handler(commands=['deposit'])
async def depositMoney(message: types.Message):
    # Create InlineKeyboardMarkup with 1 button
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Stripe", callback_data='methodStripe')
    keyboard.add(button)

    # Send message with button
    await bot.send_message(message.chat.id, "Choose a payment method", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'methodStripe')
async def stripePriceList(callback_query: types.CallbackQuery):

    # Create InlineKeyboardMarkup with 5 buttons
    keyboard = types.InlineKeyboardMarkup(row_width=2)


    button1 = types.InlineKeyboardButton("3$", callback_data='3')
    button2 = types.InlineKeyboardButton("5$", callback_data='5')
    button3 = types.InlineKeyboardButton("10$", callback_data='10')
    button4 = types.InlineKeyboardButton("25$", callback_data='25')
    button5 = types.InlineKeyboardButton("50$", callback_data='50')

    keyboard.add(button1, button2, button3, button4, button5)

    # Send message with buttons
    await bot.send_message(callback_query.from_user.id, "Choose the amount of replenishment", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == '3')
async def stripePriceList(callback_query: types.CallbackQuery):
    print(3)

@dp.callback_query_handler(lambda c: c.data == '5')
async def stripePriceList(callback_query: types.CallbackQuery):
    print(5)

@dp.callback_query_handler(lambda c: c.data == '10')
async def stripePriceList(callback_query: types.CallbackQuery):
    print(10)

@dp.callback_query_handler(lambda c: c.data == '25')
async def stripePriceList(callback_query: types.CallbackQuery):
    print(25)

@dp.callback_query_handler(lambda c: c.data == '50')
async def stripePriceList(callback_query: types.CallbackQuery):
    print(50)


async def checkBalance(message, price):
    user_id = message.chat.id

    # get balance from database
    user_id = message.from_user.id
    balance = 0
    for i in cursor.execute("SELECT * FROM users WHERE id=?", (user_id,)):
        balance = i[1]

    if balance >= price:
        return True
    else:
        return False

async def reduceValance(user_id, price):
    if await membership.check(user_id):
        # get balance from database
        balance = 0

        for i in cursor.execute("SELECT * FROM users WHERE id=?", (user_id,)):
            balance = i[1]

        cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (balance - price, user_id))
        conn.commit()

@dp.message_handler(commands=['add'])
async def addUserBalance(message: types.Message):
    if await membership.check(message.from_user.id):
        # get balance from database
        user_id = message.from_user.id
        balance = 0

        for i in cursor.execute("SELECT * FROM users WHERE id=?", (user_id,)):
            balance = i[1]

        cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (balance + 1, user_id))
        conn.commit()



@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):

    if await checkBalance(message, 0.5):
        pass
    else:
        await bot.send_message(message.chat.id, "You don't have enough money on your balance.")
        return


    photo = message.photo[-1]  # Get photo

    # Get information about photo
    file_info = await bot.get_file(photo.file_id)
    file_path = file_info.file_path
    chat_id = message.chat.id

    # Get image
    image_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"
    response = requests.get(image_url)
    if response.status_code == 200:
        # The path to the folder and file where we save the image
        save_folder = 'input'
        file_name = 's' + str(message.chat.id) + '.png'
        file_path = os.path.join(save_folder, file_name)

        if os.path.isfile(file_path):
            file_name1 = 'g' + str(chat_id) + '.png'
            file_path1 = os.path.join(save_folder, file_name1)
            with open(file_path1, 'wb') as f:
                f.write(response.content)

            file_name2 = str(chat_id) + '.png'
            file_path2 = os.path.join('output', file_name2)
            with open(file_path2, 'wb') as f:
                f.write(response.content)

            await bot.send_message(chat_id, "Wait for your request to be processed! ⏳")

            roop.ui.select_source_path(file_path)
            roop.ui.select_target_path(file_path1)
            roop.ui.select_output_path(file_path2)
            from roop.core import run
            run()

            with open(file_path2, 'rb') as f:
                await bot.send_photo(chat_id=chat_id, photo=f, caption="Great, here's your processed photo! ✅")
                await reduceValance(chat_id, 0.5)
                await sendUserBalance(message)


            os.remove(file_path)
            os.remove(file_path1)
            os.remove(file_path2)

            print(1)
        else:
            # Save image
            with open(file_path, 'wb') as f:
                f.write(response.content)
            await bot.send_message(chat_id, "Now, send me target video or photo!")


    else:
        await message.reply("An error occurred while uploading the image.")

@dp.message_handler(content_types=types.ContentType.ANIMATION)
async def handle_animation(message: types.Message):
    if await checkBalance(message, 1):
        pass
    else:
        await bot.send_message(message.chat.id, "You don't have enough money on your balance.")
        return

    # get video from message
    video = message.animation

    video_size = video.file_size / (1024 * 1024)
    if (video_size >= 20):
        file_name = 's' + str(message.chat.id) + '.png'
        file_path = os.path.join('input', file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
        await bot.send_message(message.chat.id, "The video size exceeds 20 MB. Submit a smaller video")
        return

    # Get information about video
    file_info = await bot.get_file(video.file_id)
    file_path = file_info.file_path
    chat_id = message.chat.id


    video_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"
    response = requests.get(video_url)
    if response.status_code == 200:
        # The path to the folder and file where we save the video
        save_folder = 'input'
        file_name = 's' + str(message.chat.id) + '.png'
        file_path = os.path.join(save_folder, file_name)

        if os.path.isfile(file_path):
            file_name1 = 'g' + str(chat_id) + '.mp4'
            file_path1 = os.path.join(save_folder, file_name1)
            with open(file_path1, 'wb') as f:
                f.write(response.content)

            file_name2 = str(chat_id) + '.mp4'
            file_path2 = os.path.join('output', file_name2)
            with open(file_path2, 'wb') as f:
                f.write(response.content)

            await bot.send_message(chat_id, "Wait for your request to be processed! ⏳")

            roop.ui.select_source_path(file_path)
            roop.ui.select_target_path(file_path1)
            roop.ui.select_output_path(file_path2)
            from roop.core import run
            run()

            with open(file_path2, 'rb') as f:
                await bot.send_video(chat_id=chat_id, video=f, caption="Great, here's your processed video! ✅")
                await reduceValance(chat_id, 1)
                await sendUserBalance(message)

            os.remove(file_path)
            os.remove(file_path1)
            os.remove(file_path2)

            print(1)
        else:

            await bot.send_message(chat_id, "Send the source photo first!")



@dp.message_handler(content_types=types.ContentType.VIDEO)
async def handle_video(message: types.Message):

    if await checkBalance(message, 0.5):
        pass
    else:
        await bot.send_message(message.chat.id, "You don't have enough money on your balance.")
        return

    # Get video from message
    video = message.video

    #Check video size
    video_size = video.file_size / (1024 * 1024)
    if (video_size >= 20):
        file_name = 's' + str(message.chat.id) + '.png'
        file_path = os.path.join('input', file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
        await bot.send_message(message.chat.id, "The video size exceeds 20 MB. Submit a smaller video")
        return

    # get information about photo
    file_info = await bot.get_file(video.file_id)
    file_path = file_info.file_path
    chat_id = message.chat.id

    image_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"
    response = requests.get(image_url)
    if response.status_code == 200:

        save_folder = 'input'
        file_name = 's' + str(message.chat.id) + '.png'
        file_path = os.path.join(save_folder, file_name)

        if os.path.isfile(file_path):
            file_name1 = 'g' + str(chat_id) + '.mp4'
            file_path1 = os.path.join(save_folder, file_name1)
            with open(file_path1, 'wb') as f:
                f.write(response.content)

            file_name2 = str(chat_id) + '.mp4'
            file_path2 = os.path.join('output', file_name2)
            with open(file_path2, 'wb') as f:
                f.write(response.content)

            await bot.send_message(chat_id, "Wait for your request to be processed! ⏳")

            roop.ui.select_source_path(file_path)
            roop.ui.select_target_path(file_path1)
            roop.ui.select_output_path(file_path2)
            from roop.core import run
            run()

            with open(file_path2, 'rb') as f:
                await bot.send_video(chat_id=chat_id, video=f, caption="Great, here's your processed video! ✅")
                await reduceValance(chat_id, 1)
                await sendUserBalance(message)

            os.remove(file_path)
            os.remove(file_path1)
            os.remove(file_path2)

            print(1)
        else:

            await bot.send_message(chat_id, "Send the source photo first!")


if __name__ == '__main__':

    executor.start_polling(dp)