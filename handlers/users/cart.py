from loader import dp, db
from aiogram import types
from aiogram.dispatcher import FSMContext

@dp.message_handler(text="Savatcha 🛒", state="*")
async def get_cart(message: types.Message, state: FSMContext):
    cart = await db.select_cart_product()