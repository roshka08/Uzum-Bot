from loader import db, dp
from aiogram import types
from states.shop_state import ShopState
from keyboards.default.main import numbers_markup
from aiogram.dispatcher import FSMContext

@dp.message_handler(state=ShopState.product)
async def send_product(message: types.Message, state: FSMContext):
    product = await db.select_product(title=message.text)
    await state.update_data(data={"cat_id": product['cat_id'], "product_id": product['id']})
    markup = await numbers_markup()
    image = product['image']
    caption = f"<b>{product['title']} - {product['price']}$</b> \n\n<i>{product['description']}</i>"
    await message.answer_photo(photo=image, caption=caption, reply_markup=markup)
    await ShopState.next()