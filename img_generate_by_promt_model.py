import torch
from diffusers import DiffusionPipeline

# Функция инициализации модели генерации картинки из промта
def initialize_img_generation_model():
    pipeline = DiffusionPipeline.from_pretrained(
        'darkstorm2150/Protogen_Infinity_Official_Release',
        torch_dtype=torch.float16,
    )
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    pipeline = pipeline.to(device)
    return pipeline

pipeline = initialize_img_generation_model()


