import os
import random
from pathlib import Path
from typing import Any

import numpy as np
from keras import activations
from keras.layers import (Activation, BatchNormalization, Conv1D,
                          Conv1DTranspose, Dense, Dropout, Flatten,
                          GaussianNoise, LeakyReLU, Reshape)
from keras.models import Sequential, load_model
from keras.optimizers import Adam
from midi.decode import get_array_of_notes
from midi.encode import get_file_from_standard_features
from sklearn.utils import shuffle

from models.music_model import MusicModel, ProgressCallback, ProgressMetadata

AVG = 512  # length of generated array

OFFSET = 256

LATENT_DIM = 16  # dimension of latent space
# higher LATENT_DIM -> samples produced by generator converge more to dataset

REAL_MULTIPLIER = 0.85  # multiplier of real samples [0; 1];
# if it's closer to 0, discriminator will struggle to distinguish real and fake samples more

SAVE_STEP = 100

THRESHOLD = 0.7  # threshold of probability while generating a midi file
# GAN generates probabilities that note is on during specific time unit

N_BATCH = 32

DISC_BATCH = 2

DISC_SAMPLES = 8

GLOBAL_SEED = 2137


class GAN(MusicModel):
    model: Sequential
    discriminator: Sequential
    generator: Sequential
    data: np.ndarray

    def __init__(self) -> None:
        self.data = np.zeros((0, AVG, 128), dtype=np.float16)
        self.discriminator = self.define_discriminator()
        self.generator = self.define_generator(LATENT_DIM)
        self.model = self.define_gan(self.generator, self.discriminator)

    def prepare_data(self, midi_file: Path) -> tuple[Any, Any]:
        data_lines = get_array_of_notes(midi_file, False, True)
        assert data_lines.shape[1] == 128, "Incorrect number of notes (expected: 128)"

        for i in range(data_lines.shape[0]//OFFSET - 1):
            # maximum number of samples
            if (self.data.shape[0] > 5000):
                break
            data_processed = np.zeros((1, AVG, 128))
            # divide data into chunks (AVG x 128)
            if (data_lines.shape[0]) > AVG*(i+1):
                data_processed[0] = data_lines[AVG*i: AVG*(i+1), ]

            self.data = np.array(np.append(self.data, data_processed, axis=0), dtype=np.float16)

        # y: 1 - the image is real, 0 - the image is fake
        return data_lines, 1

    def postprocess_array(self, array: np.ndarray) -> np.ndarray:
        if array.shape[1] != 128:
            array = np.swapaxes(array, 0, 1)

        if array.shape == (AVG, 128):
            array = array[:, ~np.isnan(array).any(axis=0)]
        else:
            return np.zeros(1)
        if np.max(array) == np.min(array):
            out = array - np.min(array)
        else:
            out = (array - np.min(array)) / (np.max(array) - np.min(array))
        out[out < THRESHOLD] = 0
        out *= 128

        return out

    def create_dataset(self, dataset: list[tuple[Any, Any]]) -> tuple[Any, Any]:
        return self.data, np.ones(len(dataset))

    def model_summary(self) -> str:
        return self.model.summary() + self.generator.summary() + self.discriminator.summary()

    def save(self, path: Path) -> None:
        self.model.save(path, save_format='h5')

    def save_npy(self, prediction: np.ndarray, save_path: Path | None, save_name: str) -> None:

        if np.sum(prediction) == 0:
            print("You want to save an empty file")

        if save_path is not None:
            os.makedirs(save_path, exist_ok=True)
            np.save('{}/{}'.format(save_path, save_name), prediction)

    def load(self, path: Path) -> None:
        # path to GAN defined exactly like in define_gan
        self.model = load_model(path)
        assert len(
            self.model.layers) == 3 and self.model.layers[0].name == 'generator' and self.model.layers[1].name == 'discriminator', "Incorrect model."

        self.generator = self.model.get_layer('generator')
        self.discriminator = self.model.get_layer('discriminator')

    def define_discriminator(self) -> Sequential:
        model = Sequential()
        filters = AVG * 2
        model.add(GaussianNoise(0.1))

        model.add(Conv1D(filters//4, 3, strides=8, padding='same'))
        model.add(LeakyReLU(alpha=0.2))

        model.add(Conv1D(filters//4, 3, strides=8, padding='same'))
        model.add(LeakyReLU(alpha=0.2))

        model.add(Flatten())
        model.add(Dropout(0.4))
        model.add(BatchNormalization())
        model.add(Dense(1, activation='sigmoid'))

        opt = Adam(learning_rate=0.0001, beta_1=0.5)
        model.compile(loss='binary_crossentropy', optimizer=opt, metrics=[
                      'binary_accuracy', 'Precision', 'Recall', 'AUC'])
        return model

    def define_generator(self, latent_dim: int) -> Sequential:
        start_height = 128 // 8
        start_width = AVG // 8
        filters = AVG * 2
        model = Sequential()

        n_nodes = start_width * start_height
        model.add(Dense(n_nodes, input_dim=latent_dim))

        model.add(LeakyReLU(alpha=0.2))
        model.add(Reshape((4, n_nodes//4)))

        model.add(BatchNormalization())

        model.add(Conv1DTranspose(filters//2, 3, strides=8, padding='same'))
        model.add(LeakyReLU(alpha=0.2))

        model.add(Conv1DTranspose(filters//4, 3, strides=8, padding='same'))
        model.add(LeakyReLU(alpha=0.2))

        model.add(Dropout(0.4))
        model.add(Reshape((128, AVG)))

        model.add(Activation(activations.tanh))
        return model

    def define_gan(self, g_model: Sequential, d_model: Sequential, loss: str = 'binary_crossentropy',
                   optimizer: Any = None) -> Sequential:
        d_model.trainable = False
        model = Sequential()

        model.add(g_model)
        model.layers[0]._name = 'generator'

        model.add(d_model)
        model.layers[1]._name = 'discriminator'

        if not optimizer:
            optimizer = Adam(learning_rate=0.0001, beta_1=0.5)
        model.compile(loss=loss, optimizer=optimizer, metrics=['binary_accuracy', 'Precision', 'Recall', 'AUC'])
        model.add(Flatten())

        return model

    def generate_real_samples(self, dataset: np.ndarray, n_samples: int) -> tuple[Any, Any]:
        ix = np.random.randint(0, len(dataset), n_samples)
        x = np.array(dataset)[ix]
        for i in range(ix.shape[0]):
            x[i] = np.asarray(x[i], dtype=np.float16)

        y = np.ones((n_samples, 1))

        return np.swapaxes(np.asarray(x), 1, 2), y

    def generate_latent_points(self, latent_dim: int, n_samples: int, seed: int) -> np.ndarray:
        x_input = np.random.randint(2, size=latent_dim * n_samples)
        x_input = x_input.reshape(n_samples, latent_dim)

        return x_input

    def generate_fake_samples(self, generator: Sequential, latent_dim: int, n_samples: int, seed: int) \
            -> tuple[np.ndarray, np.ndarray]:
        x_input = self.generate_latent_points(latent_dim, n_samples, seed)
        x = generator.predict(x_input)
        out = (x - np.min(x)) / (np.max(x) - np.min(x))

        x[out < THRESHOLD] = 0
        x[out >= THRESHOLD] = 1

        y = np.zeros((n_samples, 1))

        return x, y

    def save_models(self, save_path: Path, gan: Sequential, step: int) -> None:
        save_gan_path = save_path.joinpath('gan_models')
        save_gan_path.mkdir(exist_ok=True, parents=True)
        gan.save(save_gan_path.joinpath(f'gan_model{step}.h5'))

    def train(self, epochs: int | None, x_train: Any, y_train: Any, progress_callback: ProgressCallback,
              checkpoint_path: Path | None = None) -> None:
        epochs = epochs or 10
        batch_per_epoch = len(x_train) // N_BATCH
        n_steps = batch_per_epoch * epochs

        for step in range(n_steps):
            for k in range(DISC_BATCH):
                x_real, y_real = self.generate_real_samples(self.data, N_BATCH)
                x_fake, y_fake = self.generate_fake_samples(self.generator, LATENT_DIM, N_BATCH, GLOBAL_SEED)
                d_loss1 = self.discriminator.train_on_batch(x_fake, y_fake)
                d_loss2 = self.discriminator.train_on_batch(x_real, y_real)
                d_loss = np.asarray((np.asarray(d_loss1) + np.asarray(d_loss2))/2)

            z_input = self.generate_latent_points(LATENT_DIM, N_BATCH, GLOBAL_SEED)
            y_real2 = np.ones((N_BATCH, 1)) * random.uniform(REAL_MULTIPLIER, 1.0)
            g_loss = self.model.train_on_batch(z_input, y_real2)

            x, y = self.generate_fake_samples(self.generator, LATENT_DIM, 25, GLOBAL_SEED)

            epoch = (step + 1) // batch_per_epoch

            if step == 0 or step % batch_per_epoch == batch_per_epoch-1:
                x_real, y_real = self.generate_real_samples(self.data, N_BATCH)
                x_fake, y_fake = self.generate_fake_samples(self.generator, LATENT_DIM, N_BATCH, GLOBAL_SEED)
                y_fake = np.ones(y_fake.shape)
                acc_y = np.round(self.discriminator.predict(x_fake))
                acc = np.sum(acc_y) / np.sum(y_fake)
                g_loss = self.discriminator.evaluate(x_fake, y_fake)
                y_fake = np.zeros(y_fake.shape)
                y_real = np.ones(y_real.shape)
                x_fake, y_fake = self.generate_fake_samples(self.generator, LATENT_DIM, N_BATCH, GLOBAL_SEED)
                x, y = np.vstack((x_real, x_fake)), np.vstack((y_real, y_fake))
                x, y = shuffle(x, y)
                d_loss = self.discriminator.evaluate(x, y)
                print('epoch: %d, discriminator_loss=%.3f,  generator_loss=%.3f \n'
                      % (epoch, d_loss[0],  g_loss[0]))
                progress_callback([(epoch, d_loss[0]), (epoch, g_loss[0])])

            if step % SAVE_STEP == 0:
                self.save_npy(self.postprocess_array(x_fake[0]), checkpoint_path, str(step))
                # if checkpoint_path is not None:
                #     self.save_models(checkpoint_path, self.model, step)

    def generate(self, path: Path, seed: int | None = None) -> None:
        if (isinstance(seed, int)):
            x_fake, y_fake = self.generate_fake_samples(self.generator, LATENT_DIM, 1, seed)
        else:
            x_fake, y_fake = self.generate_fake_samples(self.generator, LATENT_DIM, 1, GLOBAL_SEED)

        x_array = self.postprocess_array(x_fake[0])
        get_file_from_standard_features(x_array, 500000, path, True, False, False)

    @staticmethod
    def get_progress_metadata() -> ProgressMetadata:
        return ProgressMetadata(x_label='Epoch', y_label='Loss', legends=['Discriminator loss', 'Generator loss'])
