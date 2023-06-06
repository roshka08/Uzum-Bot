from aiogram.types import ShippingOption, LabeledPrice

REGULAR_SHIPPING = ShippingOption(
    id="regular",
    title="3 kunda yetkazib berish",
    prices=[
        LabeledPrice(label="Maxsus quti", amount=1000000)
    ]
)

FAST_SHIPPING = ShippingOption(
    id="fast",
    title="1 kunda yetkazib berish",
    prices=[
        LabeledPrice(label="Tezkor etkazib narxi", amount=2000000)
    ]
)

PICKUP_SHIPPING = ShippingOption(
    id="pickup",
    title="Do'kondan olib ketish",
    prices=[
        LabeledPrice(label="Do'kondan olib ketish", amount=-5000000)
    ]
)