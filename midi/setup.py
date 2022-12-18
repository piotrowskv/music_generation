from setuptools import setup

setup(
    name='midi',
    version='1.0',
    packages=['midi'],
    install_requires=[
        'music21',
        'mido',
        'requests',
        'tqdm',
        'numpy==1.23.5',
    ],
)
