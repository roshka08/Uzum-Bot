from loader import dp, db, bot
from aiogram import types
from states.shop_state import ShopState
from aiogram.dispatcher import FSMContext
from handlers.users.cart import get_cart_info
from keyboards.default.main import make_order_markup, get_category_markup, make_order_location_markup, main_markup
from utils.misc.products import InVoice
from aiogram.types import LabeledPrice
from utils.misc.shipping_option import REGULAR_SHIPPING, FAST_SHIPPING, PICKUP_SHIPPING
from data.config import ADMINS

async def send_invoice(products):
    total_prices = [
        LabeledPrice(label="Yetkazib berish narxi", amount=5000000)
    ]

    description = "Quyidagi mahsulotlar uchun to'lov qilishingiz kerak, "

    for item in products:
        product = await db.select_product(id=item["product_id"])
        description += f"{product['title']}, "
        total_prices.append(LabeledPrice(label=product['title'], amount=int(product['price'] * 100) * item["amount"]))

    invoice = InVoice(
        title="To'lov qilish uchun quyidagi tugmani bosing!",
        description=description, 
        currency="UZS",
        prices=total_prices,
        start_parameter="create_invoice",
        need_email=True,
        need_name=True,
        need_phone_number=True,
        need_shipping_address=True,
        is_flexible=True,
    )
    return invoice

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
    lon = message.location.longitude
    await db.add_order(user_id=user["id"], phone_number=str(phone_number), lat=str(lat), lon=str(lon), total_price=total_prices, paid=False)
    orders = await db.select_all_orders(user_id=user["id"])
    orders_id = orders[-1]["id"]
    cart_items = await db.select_all_cart_items(user_id=user["id"])
    for item in cart_items:
        product_id = item['product_id']
        amount = item["amount"]
        await db.add_order_product(order_id=orders_id, product_id=product_id, amount=amount)
    await db.clear_cart_item(user_id=user['id'])
    await message.answer("Buyurtmangiz saqlandi tez orada siz bilan bog'lanamiz!", reply_markup=main_markup)
    invoice = await send_invoice(products=cart_items)
    await bot.send_invoice(chat_id=message.from_user.id, **invoice.generate_invoice(), payload="payload:order")
    await state.update_data(data={"order_id": orders_id})

@dp.shipping_query_handler()
async def choose_shipping(query: types.ShippingQuery):
    if query.shipping_address.country_code != "UZ":
        await bot.answer_shipping_query(shipping_query_id=query.id, ok=False, error_message="Chet elga yetkazib bera olmaymiz")
    elif query.shipping_address.city.lower() == "Urganch":
        await bot.answer_shipping_query(shipping_query_id=query.id, shipping_options=[FAST_SHIPPING, REGULAR_SHIPPING, PICKUP_SHIPPING], ok=True)
    else:
        await bot.answer_shipping_query(shipping_query_id=query.id, shipping_options=[FAST_SHIPPING, REGULAR_SHIPPING], ok=True)

@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pro_checkout_query: types.PreCheckoutQuery, state: FSMContext):
    data = await state.get_data()
    order_id = data.get('order_id')
    order_product = await db.select_order_product(order_id=order_id)
    text = "Quyidagi mahsulot buyurtma berildi:\n"

    for item in order_product:
        product_id = item['product_id']
        amount = item['amount']
        product = await db.select_product(id=product_id)
        text += f"{product['title']} x {amount}\n"

    await db.update_order_paid(order_id=order_id, paid=True)
    await bot.answer_pre_checkout_query(pre_checkout_query_id=pro_checkout_query.id, ok=True)
    await bot.send_message(chat_id=pro_checkout_query.from_user.id, text="xaridingiz uchun rahmat!")
    await bot.send_message(chat_id=ADMINS[0], text=f"ID: {pro_checkout_query.id}\n"
                                                    f"Payload: {pro_checkout_query.invoice_payload}\n"
                                                    f"Telegram user: {pro_checkout_query.from_user.first_name}\n"
                                                    f"Xaridor: {pro_checkout_query.order_info.name}, tel: {pro_checkout_query.order_info.phone_number}" + text)
    await state.finish()