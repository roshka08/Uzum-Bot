from loader import db
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

back_button = KeyboardButton(text="⬅️ Orqaga")
back_main_button = KeyboardButton(text="🏠 Bosh menyu")
cart_button = KeyboardButton(text="Savatcha 🛒")
check_out_button = KeyboardButton(text="Rasmiylashtirish 🛒")
clear_button = KeyboardButton(text="🔄 Tozalash")

main_markup = ReplyKeyboardMarkup(resize_keyboard=True)
main_markup.add(KeyboardButton(text="Mahsulotlarimiz 🛍"))
main_markup.row(cart_button, check_out_button)
main_markup.add(KeyboardButton(text="Buyurtmalarim 📕"))


async def get_category_markup():
    categories = await db.select_all_cats()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for category in categories:
        markup.insert(KeyboardButton(text=category["title"]))
    markup.add(cart_button, check_out_button)
    markup.add(back_button, back_main_button)
    return markup

async def get_product_markup(products):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for product in products:
        markup.insert(KeyboardButton(text=product['title']))
    markup.add(cart_button, check_out_button)
    markup.add(back_button, back_main_button)
    return markup

async def numbers_markup(number=9):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for i in range(1, number + 1):
        markup.insert(KeyboardButton(text=str(i)))
    markup.add(cart_button, back_button)
    return markup

async def cart_items_markup(products):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for product in products:
        markup.insert(KeyboardButton(text=f"❌ {product} ❌"))
    markup.add(check_out_button)
    markup.row(back_button, clear_button)
    return markup

async def make_order_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton(text="📞 Telefon raqamingizni tasdiqlash", request_contact=True))
    markup.row(back_button)
    return markup

async def make_order_location_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton(text="📍 Manzilni yuborish", request_location=True))
    markup.row(back_button)
    return markup