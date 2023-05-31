from loader import db, dp
from aiogram import types
from keyboards.default.main import get_product_markup, get_category_markup
from states.shop_state import ShopState

@dp.message_handler(state=ShopState.category)
async def get_product(message: types.Message):
    category = await db.select_category(title=message.text)
    if category:
        products = await db.select_product_by_category(cat_id=category['id'])
        if products:
            markup = await get_product_markup(products=products)
            await message.answer(f"{category['title']} bo'limidan kerakli mahsulotni tanlang", reply_markup=markup)
            await ShopState.next()
        else:
            await message.answer(f"{category['title']} bo'limida hozircha mahsulotlar mavjud emas!")
    else:
        markup = await get_category_markup()
        await message.answer("Quydagi kategoriyalardan birini tanlang", reply_markup=markup) 