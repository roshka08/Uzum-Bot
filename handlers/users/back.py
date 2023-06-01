from loader import dp, db
from aiogram import types
from states.shop_state import ShopState
from keyboards.default.main import main_markup, get_category_markup, get_product_markup
from aiogram.dispatcher import FSMContext

@dp.message_handler(text="🏠 Bosh menyu", state="*")
@dp.message_handler(text="⬅️ Orqaga", state=ShopState.category)
async def main_menu_redirect(message: types.Message, state: FSMContext):
    await message.answer("Siz bosh menyuga qaytingiz. Kerakli bo'limni tanlang!", reply_markup=main_markup)
    await state.finish()

@dp.message_handler(text="⬅️ Orqaga", state=ShopState.product)
async def category_menu_redirect(message: types.Message):
    markup = await get_category_markup()
    await message.answer("Kerakli kategoriyani tanlang", reply_markup=markup)
    await ShopState.category.set()

@dp.message_handler(text="⬅️ Orqaga", state=ShopState.amount)
async def product_menu_redirect(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cat_id = data.get('cat_id')
    products = await db.select_product_by_category(cat_id=cat_id)
    markup = await get_product_markup(products=products)
    await message.answer(f"Ushbu bo'limidan kerakli mahsulotni tanlang", reply_markup=markup)
    await ShopState.product.set()