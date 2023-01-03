from enum import Enum

from app.dto.models import ModelVariant


class SupportedModels(Enum):
    LSTM = ModelVariant(
        id='0f5e5af5-9ede-4cc8-814d-f7a0dfb8a6d6',
        name='LSTM',
        description='Sequential model generating each timestep one by one.')
    MARKOV = ModelVariant(
        id='e5893ba5-1cd1-4153-ac56-6b5898897503',
        name='Markov Chain',
        description='Statistical model generating most probable notes.')
    GAN = ModelVariant(
        id='eafdabd3-fe56-474d-91be-7a9eeeed2124',
        name='GAN',
        description='Generative model generating the whole song at once.')
