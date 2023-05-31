from loader import db
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_markup = ReplyKeyboardMarkup(resize_keyboard=True)
main_markup.add(KeyboardButton(text="Mahsulotlarimiz 🛍"))
main_markup.row("Savatcha 🛒", "Savatcha 🛒")
main_markup.add(KeyboardButton(text="Mening Hamyonim 💰"))

back_button = KeyboardButton(text="⬅️ Orqaga")
back_main_button = KeyboardButton(text="🏠 Bosh menyu")


async def get_category_markup():
    categories = await db.select_all_cats()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for category in categories:
        markup.insert(KeyboardButton(text=category["title"]))
    return markup

async def get_product_markup(products):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for product in products:
        markup.insert(KeyboardButton(text=product['title']))
    return markup

async def numbers_markup(number=9):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for i in range(1, number + 1):
        markup.insert(KeyboardButton(text=str(i)))
    return markup