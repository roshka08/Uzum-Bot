from loader import dp, db
from aiogram import types
from states.shop_state import ShopState
from aiogram.dispatcher import FSMContext
from handlers.users.cart import get_cart_info
from keyboards.default.main import make_order_markup, get_category_markup, make_order_location_markup, main_markup

@dp.message_handler(text="Rasmiylashtirish 🛒", state="*")
async def make_order(message: types.Message, state: FSMContext):
    user = await db.select_user(telegram_id=message.from_user.id)
    cart_items = await db.select_all_cart_items(user_id=user["id"])
    if cart_items:
        msg = await get_cart_info(cart_items=cart_items)
        await state.update_data(data={"total_price": msg[2]})
        markup = await make_order_markup()
        await message.answer(msg[0], reply_markup=markup)
        await ShopState.phone_number.set()
    else:
        markup = await get_category_markup()
        await message.answer("Uzur siz buyurtmani rasmiylashtira olmaysiz, oldin savatingizga mahsulot qo'shing!", reply_markup=markup)
        await ShopState.category.set()

@dp.message_handler(content_types=["contact"], state=ShopState.phone_number)
async def get_phone_number(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(data={"phone_number": phone})
    markup = await make_order_location_markup()
    await message.answer("Xozirgi manzilingizni yuboring", reply_markup=markup)
    await ShopState.location.set()

@dp.message_handler(content_types=["location"], state=ShopState.location)
async def get_location(message: types.Message, state: FSMContext):
    user = await db.select_user(telegram_id=message.from_user.id)
    data = await state.get_data()
    total_prices = data.get('total_price')
    phone_number = data.get('phone_number')
    lat = message.location.latitude
    long = message.location.longitude
    await db.add_order(user_id=user["id"], phone_number=str(phone_number), lat=str(lat), lon=str(long), total_price=total_prices, paid=False)
    orders = await db.select_all_orders(user_id=user["id"])
    orders_id = orders[-1]["id"]
    cart_items = await db.select_all_cart_items(user_id=user["id"])
    for item in cart_items:
        product_id = item['product_id']
        amount = item["amount"]
        await db.add_order_product(order_id=orders_id, product_id=product_id, amount=amount)
    await db.clear_cart_item(user_id=user['id'])
    await message.answer("Buyurtmangiz saqlandi tez orada siz bilan bog'lanamiz!", reply_markup=main_markup)
    await state.finish()