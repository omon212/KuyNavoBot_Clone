from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Guruhga qo'shish ⤴️", callback_data="add_group_bot")
        ]
    ]
)
