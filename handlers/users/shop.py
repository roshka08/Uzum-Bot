from loader import db, dp
from aiogram import types
from keyboards.default.main import get_category_markup
from states.shop_state import ShopState

@dp.message_handler(text="Mahsulotlarimiz 🛍")
async def get_catalog(message: types.Message):
    markup = await get_category_markup()
    await message.answer("Kerakli kategoriyani tanlang", reply_markup=markup)
    await ShopState.category.set()