from enum import Enum

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dto import models as m

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SupportedModels(Enum):
    LSTM = m.ModelVariant(
        id='0f5e5af5-9ede-4cc8-814d-f7a0dfb8a6d6',
        name='LSTM',
        description='Sequential model generating each timestep one by one.')
    MARKOV = m.ModelVariant(
        id='e5893ba5-1cd1-4153-ac56-6b5898897503',
        name='Markov Chain',
        description='Statistical model generating most probable notes.')
    GAN = m.ModelVariant(
        id='eafdabd3-fe56-474d-91be-7a9eeeed2124',
        name='GAN',
        description='Generative model generating the whole song at once.')


@app.get("/models", response_model=m.ModelVariants)
def get_models() -> m.ModelVariants:
    models = [e.value for e in SupportedModels]

    return m.ModelVariants(models)
