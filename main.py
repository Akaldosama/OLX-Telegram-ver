# online market bot registration, photo, product, get, put, delete, sold. 9.24
import asyncio

import aiohttp
from aiogram import Bot, Dispatcher, executor, types
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import requests
from aiogram.types import ContentType
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Command
from aiogram import types
import re

url = 'https://7f51-213-230-80-71.ngrok-free.app'
TOKEN = '7758239108:AAHnLTmadRdpfe4C60V6-5P_0b2RvqpGrAU'
URL_REGISTRATION = f'{url}/registration/'
URL_PRODUCT_TYPES = f'{url}/product-types/'
URL_PRODUCTS = f'{url}/products/'
URL_ADD_TO_CART = f'{url}/cart/'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class RegistrationStates(StatesGroup):
    fullname = State()
    phone = State()


class ProductStates(StatesGroup):
    product = State()


class PostProductStates(StatesGroup):
    photo = State()
    title = State()
    description = State()
    price = State()
    type = State()


# =======================================================================================================================================
# @dp.message_handler(commands=['start'], state='*')
# async def start(message: types.Message):
#     telegram_id = str(message.from_user.id)
#     check_response = requests.post(URL_REGISTRATION, json={"telegram_id": telegram_id})
#
#     if check_response.status_code in (200, 201):
#         data = check_response.json()
#         if data['is_registered']:
#             await message.answer(
#                 f"Hello, {data['fullname']}!\nChoose operation: /products, /post_product, /myproducts, /cart"
#             )
#         else:
#             await message.answer(
#                 "We are excited to have you here.\nYou can browse through our amazing collection of products and place orders with ease.\nBefore you start you need to be registered!!!\n\nHappy shopping! 🛍️")
#             await asyncio.sleep(1)
#             await message.answer('For registration Please enter your fullname:')
#             await RegistrationStates.fullname.set()
#     else:
#         await message.answer("Something went wrong. Please, try again. \n\t\t/start")
#
#
#
# @dp.message_handler(state=RegistrationStates.fullname)
# async def get_fullname(message: types.Message, state: FSMContext):
#     await state.update_data(fullname=message.text)
#     await message.answer('Enter your phone number (+998999999999).')
#     await RegistrationStates.phone.set()
#
#
# @dp.message_handler(state=RegistrationStates.phone)
# async def get_phone(message: types.Message, state: FSMContext):
#     await state.update_data(phone=message.text)
#
#     user_data = await state.get_data()
#     telegram_id = str(message.from_user.id)
#     fullname = user_data['fullname']
#     phone = user_data['phone']
#
#     payload = {
#         "telegram_id": telegram_id,
#         "fullname": fullname,
#         "phone": phone
#     }
#
#     response = requests.post(URL_REGISTRATION, json=payload)
#     if response.status_code in (200, 201):
#         await message.answer('You have been registered successfully🎉\n\nType /start again')
#     else:
#         error_message = response.json().get('error', 'Something went wrong 👎.')
#         await message.answer(f"Error: {error_message}")
#
#     await state.finish()


# ===============================================================================================================================================


# Util function to check registration
async def is_registered(telegram_id):
    response = requests.post(URL_REGISTRATION, json={"telegram_id": telegram_id})
    if response.status_code in (200, 201):
        return response.json()
    return None


@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message, state: FSMContext):
    telegram_id = str(message.from_user.id)
    data = await is_registered(telegram_id)

    if data and data['is_registered']:
        await message.answer(
            f"Hello, {data['fullname']}!\nChoose operation: /products, /post_product, /myproducts, /cart")
    else:
        await message.answer(
            "🛍️ Welcome to our store!\nTo get started, please register.\n\nEnter your full name (not a command):"
        )
        await RegistrationStates.fullname.set()


@dp.message_handler(lambda message: message.text.startswith('/'), state=RegistrationStates.fullname)
async def block_commands_in_name(message: types.Message):
    await message.answer("❌ Please enter your *full name*, not a command.")
    # Keeps the state


@dp.message_handler(state=RegistrationStates.fullname)
async def get_fullname(message: types.Message, state: FSMContext):
    await state.update_data(fullname=message.text)
    await message.answer("📱 Now enter your phone number in format: +998991234567")
    await RegistrationStates.phone.set()


@dp.message_handler(state=RegistrationStates.phone)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.text
    if not re.fullmatch(r"\+998\d{9}", phone):
        await message.answer("❌ Invalid phone number. It must be in this format: +998991234567")
        return  # Stay in current state until valid

    await state.update_data(phone=phone)

    user_data = await state.get_data()
    telegram_id = str(message.from_user.id)

    payload = {
        "telegram_id": telegram_id,
        "fullname": user_data['fullname'],
        "phone": phone
    }

    response = requests.post(URL_REGISTRATION, json=payload)
    if response.status_code in (200, 201):
        await message.answer("✅ You are now registered! Type /start again to use the bot.")
    else:
        await message.answer("⚠️ Something went wrong. Please try again later.")

    await state.finish()


@dp.message_handler(commands=['products'], state='*')
async def products(message: types.Message):
    response = requests.get(URL_PRODUCT_TYPES)
    if response.status_code == 200:
        product_types = response.json()
        types_btn = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if product_types:
            for type in product_types:
                types_btn.add(type['name'])  # Access the 'name' from the response
            types_btn.add('ALL')  # Option to view all products
            await message.answer('Choose product type:', reply_markup=types_btn)
            await ProductStates.product.set()  # Set state to remember user's choice
        else:
            await message.answer('No product types found!')
    else:
        await message.answer('Something went wrong ❌!!! Please try again /start')


async def require_registration(message: types.Message):
    telegram_id = str(message.from_user.id)
    data = await is_registered(telegram_id)
    if not data or not data['is_registered']:
        await message.answer("❗ You must register first using /start.")
        return False
    return True


# Handle when a user selects a product type (or 'ALL')
# @dp.message_handler(state=ProductStates.product, lambda message: message.text not in ['/start', '/products', '/post_product'])
@dp.message_handler(
    lambda message: message.text and message.text not in ['/start', '/products', '/post_product', '/myproducts', '/cart'],
    state=ProductStates.product
)
async def get_products(message: types.Message, state: FSMContext):
    type_product = message.text

    if not await require_registration(message):
        return

    # Construct the URL based on the selected type
    if type_product == 'ALL':
        URL_PRODUCTS = f'{url}/products/'  # URL for all products
    else:
        URL_PRODUCTS = f'{url}/products/?type={type_product}'  # URL with type filtering

    response = requests.get(URL_PRODUCTS)

    if response.status_code == 200:
        products = response.json()
        if not products:
            await message.answer("No products found.")
        else:
            for product in products:
                text = (
                    f"📦 {product['title']}\n"
                    f"💰 Price: {product['price']}\n"
                    f"📄 {product['description']}"
                )

                photo_url = product.get('photo')  # Ensure your API returns full URL or serve it from a domain

                btn = types.InlineKeyboardMarkup()
                # btn = types.InlineKeyboardButton(text='Buy', callback_data=str(product['id']))
                buy_btn = types.InlineKeyboardButton("Buy", callback_data=f"buy:{product['id']}")
                cart_btn = types.InlineKeyboardButton("Cart", callback_data=f"cart:{product['id']}")
                btn.add(cart_btn, buy_btn)

                if photo_url:
                    try:
                        await message.answer_photo(photo=photo_url, caption=text, reply_markup=btn)
                    except Exception:
                        await message.answer(text, reply_markup=btn)
                else:
                    await message.answer(text, reply_markup=btn)

            # After sending the products, allow the user to select another type
            response = requests.get(URL_PRODUCT_TYPES)
            if response.status_code == 200:
                product_types = response.json()
                types_btn = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for type in product_types:
                    types_btn.add(type['name'])
                types_btn.add('ALL')
                await message.answer("Want to see products of another type? Choose one:", reply_markup=types_btn)
                await ProductStates.product.set()  # Allow the user to reselect the type
            else:
                await message.answer("Failed to fetch product types again.")
    else:
        await message.answer("❌ Failed to fetch products.")


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('buy:'), state='*')
async def handle_buy(callback_query: types.CallbackQuery):
    product_id = callback_query.data.split(':')[1]
    telegram_id = str(callback_query.from_user.id)

    response = requests.post(f'{url}/buy/', json={
        'telegram_id': telegram_id,
        'product_id': product_id
    })

    if response.status_code == 201:
        await callback_query.answer("✅ Purchase request sent to seller.")
    else:
        try:
            error_msg = response.json()
        except Exception:
            error_msg = response.text
        await callback_query.answer(f"❌ Failed to process purchase.\n{error_msg}", show_alert=True)



@dp.callback_query_handler(lambda c: c.data.startswith('cart:'), state='*')
async def add_to_cart(callback_query: types.CallbackQuery):
    telegram_id = str(callback_query.from_user.id)
    product_id = callback_query.data.split(':')[1]

    # Send request to backend to add to cart
    response = requests.post(f'{url}/cart/', json={
        'user_telegram_id': telegram_id,
        'product_id': product_id
    })

    if response.status_code == 201:
        await callback_query.answer("✅ Added to cart.")
    else:
        await callback_query.answer("❌ Failed to add to cart.")


# ================================================================================================================================================
@dp.message_handler(commands=['post_product'], state='*')
async def post_product(message: types.Message):
    await message.answer('📸 Please send the *photo* of your product:', parse_mode='Markdown')
    await PostProductStates.photo.set()


@dp.message_handler(content_types=ContentType.PHOTO, state=PostProductStates.photo)
async def handle_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = file.file_path
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

    await state.update_data(photo_url=file_url)
    await message.answer('📝 Enter the *title* of your product:', parse_mode='Markdown')
    await PostProductStates.title.set()


@dp.message_handler(state=PostProductStates.title)
async def handle_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer('📄 Write a *description* for your product:', parse_mode='Markdown')
    await PostProductStates.description.set()


@dp.message_handler(state=PostProductStates.description)
async def handle_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer('💵 Enter the *price* (e.g. 19.99):', parse_mode='Markdown')
    await PostProductStates.price.set()


@dp.message_handler(state=PostProductStates.price)
async def handle_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price=price)
    except ValueError:
        await message.answer("❗ Invalid price format. Please enter a number.")
        return

    # Fetch product types from your API
    response = requests.get("http://127.0.0.1:8000/product-types/")
    if response.status_code == 200:
        types_data = response.json()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for t in types_data:
            markup.add(t['name'])
        await message.answer("🔘 Choose a *type* from below:", reply_markup=markup, parse_mode='Markdown')
        await PostProductStates.type.set()
    else:
        await message.answer("❌ Failed to load product types.")


@dp.message_handler(state=PostProductStates.type)
async def handle_type(message: types.Message, state: FSMContext):
    type_name = message.text

    # Fetch the product types from your API to map the type name to its id.
    type_response = requests.get(f"{url}/product-types/")
    if type_response.status_code != 200:
        await message.answer("❌ Failed to get product types.")
        await state.finish()
        return

    type_list = type_response.json()
    type_id = next((item['id'] for item in type_list if item['name'] == type_name), None)
    if not type_id:
        await message.answer("❗ Invalid type. Please choose again.")
        return

    await state.update_data(type_id=type_id)
    data = await state.get_data()

    # Get the registered user's id from the registration endpoint.
    reg_response = requests.post(URL_REGISTRATION, json={"telegram_id": str(message.from_user.id)})
    if reg_response.status_code not in (200, 201):
        await message.answer("❌ Failed to get user details.")
        await state.finish()
        return

    reg_data = reg_response.json()
    # Expecting your registration view to return the user's id as 'id'
    user_id = reg_data.get("id")
    if not user_id:
        await message.answer("❌ User ID not found. Please complete your registration.")
        await state.finish()
        return

    # Prepare the payload for the product post.
    payload = {
        "user": user_id,  # The backend expects this as a number.
        "title": data["title"],
        "description": data["description"],
        "price": data["price"],
        "type": data["type_id"],  # your API should accept this as the product type id.
        "telegram_id": str(message.from_user.id)
    }

    # Download the photo bytes from the photo URL saved in state.
    photo_url = data["photo_url"]
    async with aiohttp.ClientSession() as session:
        async with session.get(photo_url) as photo_resp:
            if photo_resp.status != 200:
                await message.answer("❌ Failed to fetch photo.")
                await state.finish()
                return
            photo_bytes = await photo_resp.read()

    # Build the multipart/form-data for the POST request.
    form = aiohttp.FormData()
    for key, value in payload.items():
        form.add_field(key, str(value))
    form.add_field("photo", photo_bytes, filename="product.jpg", content_type="image/jpeg")

    async with aiohttp.ClientSession() as session:
        async with session.post(URL_PRODUCTS, data=form) as resp:
            if resp.status == 201:
                await message.answer("✅ Product successfully posted!")
            else:
                error_text = await resp.text()
                await message.answer(f"❌ Failed to post product:\n{error_text}")

    await state.finish()


# =================================================================================================================================================

@dp.message_handler(commands=['myproducts'], state='*')
async def my_products(message: types.Message):
    telegram_id = str(message.from_user.id)
    # bot_id = '7758239108'

    # Check if the user is registered
    response = requests.get(f'{url}/user/{telegram_id}')
    if response.status_code == 200:
        user_data = response.json()
        if not user_data['is_registered']:
            await message.answer("You must register first using the '/start"
                                 "' command.")
            return

        # Fetch all products posted by the bot owner (you) (products you posted as a seller)
        response = requests.get(
            f'{url}/products?user={telegram_id}')  # Replace with your bot's telegram ID
        if response.status_code == 200:
            products = response.json()
            if products:
                for product in products:
                    text = (
                        f"📦 {product['title']}\n"
                        f"💰 Price: {product['price']}\n"
                        f"📄 {product['description']}"
                    )
                    photo_path = product.get('photo')
                    print(photo_path)  # /media/product.jpg
                    photo_url = f'{url}/{photo_path}' if photo_path else None
                    buy_btn = types.InlineKeyboardMarkup()
                    buy_btn.add(types.InlineKeyboardButton("Buy", callback_data=f"buy:{product['id']}"))
                    if photo_url:
                        try:
                            await message.answer_photo(photo=photo_url, caption=text, reply_markup=buy_btn)
                        except Exception:
                            await message.answer(text, reply_markup=buy_btn)
                    else:
                        await message.answer(text, reply_markup=buy_btn)
            else:
                await message.answer("You haven't posted any products yet.")
        else:
            await message.answer("Something went wrong while fetching your products.")
    else:

        await message.answer("Something went wrong while checking your registration. Please try again later.")


@dp.message_handler(commands=['cart'], state='*')
async def view_cart(message: types.Message):
    telegram_id = str(message.from_user.id)

    response = requests.get(f'{url}/cart/{telegram_id}/')

    if response.status_code == 200:
        cart_items = response.json()
        if not cart_items:
            await message.answer("🛒 Your cart is empty.")
        else:
            for item in cart_items:
                product = item['product']
                text = (
                    f"📦 {product['title']}\n"
                    f"💰 Price: {product['price']}\n"
                    f"📄 {product['description']}"
                )

                photo_url = product.get('photo')
                if photo_url:
                    photo_url = f"{url}{photo_url}"
                    try:
                        await message.answer_photo(photo=photo_url, caption=text)
                    except Exception:
                        await message.answer(text)
                else:
                    await message.answer(text)
    else:
        await message.answer("❌ Failed to fetch your cart.")



if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
