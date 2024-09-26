from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# Определяем разные состояние для загрузки изображения контента и стиля
class UploadState(StatesGroup):
  WAITING_FOR_CONTENT_IMG = State()
  WAITING_FOR_STYLE_IMG = State()