from loader import dp, db
from aiogram import types
from aiogram.dispatcher import FSMContext
from states.shop_state import ShopState
from keyboards.default.main import cart_items_markup, get_category_markup


async def get_cart_info(cart_items):
    total_price = 0
    msg = f"Sizning savatda 🛒:\n\n"
    products = []
    for item in cart_items:
        product_id = item['product_id']
        product = await db.select_product(id=product_id)
        price = item['amount'] * product['price']
        total_price += price
        products.append(product['title'])
        msg += f"<b>{product['title']}</b>\n{item['amount']} x {product['price']} = {price} so'm\n"
    markup = await cart_items_markup(products=products)
    msg += f"\n<b>Umumiy: </b> {total_price} so'm"
    return msg, markup, total_price

@dp.message_handler(text="Savatcha 🛒", state="*")
async def get_cart(message: types.Message):
    user = await db.select_user(telegram_id=message.from_user.id)
    cart_items = await db.select_all_cart_items(user_id=user["id"])
    if cart_items:
        msg, markup, total_price= await get_cart_info(cart_items=cart_items)
        await message.answer("«❌ Mahsulot nomi» - savatdan o'chirish\n«🔄 Tozalash» - savatni butunlay bo'shatish")
        await message.answer(msg, reply_markup=markup)
        await ShopState.cart.set()
    else:
        await message.answer("Sizning savatingiz bo'sh!")

@dp.message_handler(lambda message: "❌" in message.text, state=ShopState.cart)
async def delete_cart_item(message: types.Message):
    user = await db.select_user(telegram_id=message.from_user.id)
    product_name = " ".join(message.text.split()[1:-1])
    product = await db.select_product(title=product_name)
    await db.delete_cart_item(product_id=product["id"], user_id=user["id"])
    cart_items = await db.select_all_cart_items(user_id=user["id"])
    if cart_items:
        msg, markup, total_price= await get_cart_info(cart_items=cart_items)
        await message.answer("«❌ Mahsulot nomi» - savatdan o'chirish\n«🔄 Tozalash» - savatni butunlay bo'shatish")
        await message.answer(msg, reply_markup=markup)
        await ShopState.cart.set()
    else:
        markup = await get_category_markup()
        await message.answer("Sizning savatingiz bo'shab qoldi!", reply_markup=markup)
        await ShopState.category.set()