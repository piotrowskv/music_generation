from sys import platform

from setuptools import setup

extra_deps = ['tensorflow-macos==2.10.0',
              'tensorflow-metal==0.6.0'] if platform == "darwin" else ['tensorflow==2.10.0']

# ../midi is not listed as requirements! It is the responsibility of `models` users to also install `../midi`

setup(
    name='models',
    version='1.0',
    packages=['models'],
    install_requires=list(['numpy==1.23.5', 'keras==2.10.0', 'dataclasses-json==0.5.7',
                          'scikit-learn==1.2.0', 'matplotlib==3.6.3', *extra_deps]),
)
