from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# клавиатура под каждым фото - загрузить картинку или сгенировать
def kb_actions():
    quality_button1 = InlineKeyboardButton(text=f'Загрузить', callback_data='action_download')
    quality_button2 = InlineKeyboardButton(text=f'Сгенерировать', callback_data='action_generate')
    kb_actions = InlineKeyboardMarkup(inline_keyboard=[[quality_button1, quality_button2]], row_width=2)
    return kb_actions