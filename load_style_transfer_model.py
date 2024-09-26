import tensorflow as tf
import tensorflow_hub as hub

# Проверка доступности GPU
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)
        
# Загрузка модели переноса стиля из TensorFlow Hub
def load_style_transfer_model():
    return hub.load('C:\project\stylization_model')

hub_model = load_style_transfer_model()