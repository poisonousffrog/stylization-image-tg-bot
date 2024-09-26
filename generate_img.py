# Импортируем необходимые библиотеки
import io
import tensorflow as tf
from PIL import Image
from aiogram.types import BufferedInputFile
from deep_translator import GoogleTranslator
from typing import List

from load_style_transfer_model import hub_model
from img_generate_by_promt_model import pipeline

# переводчик на англ и словарь параметров
translator = GoogleTranslator(source='auto', target='en')

# Функция для загрузки и преобразования изображения для подачи в модель
def load_img(images_bytes):
    max_dim = 512
    img = tf.image.decode_image(images_bytes, channels=3)           # декодируем байты изображения в тензор rgb
    img = tf.image.convert_image_dtype(img, tf.float32)             # преобразуем во float32


    shape = tf.cast(tf.shape(img)[:-1], tf.float32)                 # получаем размерность изображения
    long_dim = max(shape)                                           # длинная сторона изображения
    scale = max_dim / long_dim                                      # масштаб

    new_shape = tf.cast(shape * scale, tf.int32)                    # новый размер с учетом пропорций

    img = tf.image.resize(img, new_shape)
    img = img[tf.newaxis, :]
    return img
  
  # функция для преобразования тензора изображения в байтовый поток перед отправкой пользователю
def tensor_to_image_bytes(output_img):
    # Преобразуем тензор в NumPy массив
    output_array = output_img.numpy()
    # Извлекаем изображение из батча (размерности 1)
    output_array = output_array[0]                          # Извлекаем массив размером (512, 512, 3)
    output_array = (output_array * 255).astype('uint8')     # Приводим значения из диапазона [0, 1] в диапазон [0, 255] и к типу uint8
    img = Image.fromarray(output_array)                     # Создаем изображение с помощью PIL
    # Сохраняем изображение в байтовый поток
    byte_io = io.BytesIO()
    img.save(byte_io, format='PNG')
    byte_io.seek(0)                                         # Возвращаем указатель на начало потока
    return byte_io

# функция генерации выходного стилизованного изображения и подготовка к отправке в Telegram
def processing_output_img(content_img, style_img):
  
    output_img = hub_model(tf.constant(content_img), tf.constant(style_img))[0]
    if output_img is None:
        return None
    else:
        img_bytes = tensor_to_image_bytes(output_img)               # Преобразуем изображение в байты
        image_file = BufferedInputFile(file=img_bytes.getvalue(), filename='generated_image.png') # создаем объект для отправки
        return image_file
      
# качество генерации и число картинок котоое нужно сгенерить
params = {'num_inference_steps': 20, 'num_images_per_prompt': 1}
# принимает текстовый запрос, переводит его на англ, возвращает массив картинок в виде байтов
def promt_to_image(promt: str, params: dict) -> List[bytes]:
    try:
        # перевести ру на англ
        promt = translator.translate(promt)
        # сгенерировать картинки
        image = pipeline(promt, **params, guidance_scale=3).images[0]

        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
    # если какая либо ошибка то вернуть None
    except Exception as ex:
        print(f'Ошибка: {ex}')
        image = None
    return image_bytes