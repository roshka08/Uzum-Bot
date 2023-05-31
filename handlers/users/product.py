from loader import db, dp
from aiogram import types
from states.shop_state import ShopState
from keyboards.default.main import numbers_markup

@dp.message_handler(state=ShopState.product)
async def send_product(message: types.Message):
    product = await db.select_all_product(title=message.text)
    image = product['image']
    caption = f"<b>{product['title']} - {product['price']}$</b> \n\n<i>{product['description']}</i>"
    await message.answer_photo(photo=image, caption=caption, reply_markup=numbers_markup())
    await ShopState.next()