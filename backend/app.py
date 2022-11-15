from fastapi import FastAPI

from dto.models import *

app = FastAPI()

@app.get("/models", response_model=ModelVariants)
def get_models() -> ModelVariants:
    return  ModelVariants([
        ModelVariant(
            id = '0f5e5af5-9ede-4cc8-814d-f7a0dfb8a6d6',
            name = 'LSTM',
            description = 'Sequential model generating each timestep one by one.'),
        ModelVariant(
            id = 'eafdabd3-fe56-474d-91be-7a9eeeed2124',
            name = 'GAN',
            description = 'Generative model generating the whole song at once.'),
        ])
