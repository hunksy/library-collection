from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

kb_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Поиск книги", callback_data="search_book")]
])

kb_search = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Искать по названию", callback_data="search_by_name"),],
    [InlineKeyboardButton(text="Искать по автору", callback_data="search_by_author"),],
    [InlineKeyboardButton(text="Искать по ISBN", callback_data="search_by_isbn"),],
    [InlineKeyboardButton(text="Искать по языку издания", callback_data="search_by_language"),],
]) 

arrows = [
    InlineKeyboardButton(text="⬅️", callback_data=f"languages_left"),
    InlineKeyboardButton(text="➡️", callback_data=f"languages_right")
]