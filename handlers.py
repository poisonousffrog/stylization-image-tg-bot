from aiogram import types, F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile, InputFile
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram import Router

from generate_img import load_img, processing_output_img, promt_to_image
from states import UploadState
from kb import kb_actions

router = Router()


# что делать если боту написать ему команду /start
@router.message(Command('start'))
async def start(message: types.Message, state: FSMContext):    
    await message.reply('Добро пожаловать :) \nЗдесь ты можешь загрузить исходное изображение контента или сгенерировать его по своему запросу. Аналогично ты можешь выбрать изображение стиля, которое хочешь применить к изображению контента.\n\nВыбери действие:', reply_markup=kb_actions())    
    await state.set_state(UploadState.WAITING_FOR_CONTENT_IMG)               # установить состояние на ожидание изображения контента

# обработчик нажатий на кнопки
@router.callback_query(F.data.startswith('action'))
async def handle_action(callback: types.CallbackQuery):    
    action = callback.data.split('_')[-1]                                    # Извлекаем действие, которое соответствует нажатию кнопки
    
    if action == 'download':
        await callback.answer(text=f'Отправьте изображение.')    
    elif action == 'generate':
        await callback.answer(text=f'Введите промт для генерации картинки')

# обработчик получения фото загруженного пользователем
@router.message(F.photo)
async def handle_image(message: types.Message, state: FSMContext):
    # Получаем фото максимального разрешения
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    downloaded_file = await message.bot.download_file(file_info.file_path)  # получили изображение в виде байтового объекта
    image_bytes = downloaded_file.read()                                    # чтение байтов из объекта файла фотографии

    current_state = await state.get_state()                                 # проверка текущего состояния

    if current_state == UploadState.WAITING_FOR_CONTENT_IMG:                # если ожидается изображение контента
      global content_img
      content_img = load_img(image_bytes)
      
      await state.set_state(UploadState.WAITING_FOR_STYLE_IMG)              # изменяем состояние на ожидание стиля
      await message.reply("Изображение контента загружено! Выбери действие для загрузки стилевого изображения:\n", reply_markup=kb_actions())

    elif current_state == UploadState.WAITING_FOR_STYLE_IMG:                # если ожидается изображение стиля
      global style_img, output_img
      style_img = load_img(image_bytes)
      await message.reply("Изображение загружено! \n")

      output_img = processing_output_img(content_img, style_img)            # генерация выходного изображения и подготовка к отправке
      if output_img is None:
          await message.answer('Какая-то ошибка(((')
      else:
          await message.answer_photo(photo=output_img, caption="Вот что из этого вышло")         # отправляем изображение
            
      await message.reply('\n\nЧтобы попробовать снова, выбери действие для исходного изображения контента:', reply_markup=kb_actions())      
      await state.set_state(UploadState.WAITING_FOR_CONTENT_IMG)
      
# обработчик промта для картинки
@router.message(F.text)
async def text(message: types.Message, state: FSMContext):
    params = {'num_inference_steps': 20, 'num_images_per_prompt': 1}
    image_bytes = promt_to_image(message.text, params)                      # получили поток байтов сгенерированного изобр-я
                                                                                
    if image_bytes is None:
      await message.answer('Какая-то ошибка во время генерации :(')
    else:
      image_file = BufferedInputFile(file=image_bytes, filename='image')    # файл чтобы отправить сгенерированное по запросу изображение пользователю

      current_state = await state.get_state()

      if current_state == UploadState.WAITING_FOR_CONTENT_IMG:              # если ожидается изображение контента
        await message.answer_photo(photo=image_file, caption="Изображение контента сгенерировано по твоему запросу:")
        global content_img
        content_img = load_img(image_bytes)
        await state.set_state(UploadState.WAITING_FOR_STYLE_IMG)            # изменяем состояние на ожидание стиля
        await message.reply("Выберите действие для загрузки стилевого изображения:\n", reply_markup=kb_actions())
      elif current_state == UploadState.WAITING_FOR_STYLE_IMG:              # если ожидается изображение стиля
        await message.answer_photo(photo=image_file, caption="Изображение стиля сгенерировано по твоему запросу")
        global style_img, output_img
        style_img = load_img(image_bytes)
        output_img = processing_output_img(content_img, style_img)          # генерация выходного изображения и подготовка к отправке
        if output_img is None:
            await message.answer('Какая-то ошибка :(')
        else:
            await message.answer_photo(photo=output_img, caption=f"Вот что получилось\n")           # отправляем изображение
        await message.reply('\n\nЧтобы попробовать снова, выбери действие для исходного изображения контента:', reply_markup=kb_actions())        
        await state.set_state(UploadState.WAITING_FOR_CONTENT_IMG)
