import os
import numpy as np
from typing import Any
from pathlib import Path

from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Reshape, Flatten, Dropout, LeakyReLU, Conv1D, Conv1DTranspose, Activation
from tensorflow.keras import activations

from midi.decode import get_array_of_notes
from midi.encode import get_file_from_standard_features
from models.music_model import MusicModel, ProgressCallback, ProgressMetadata, SeriesProgress

DATA_PATH = 'data'

AVG = 512  # length of generated array

LATENT_DIM = 512  # dimension of latent space
# higher LATENT_DIM -> samples produced by generator converge more to dataset

REAL_MULTIPLIER = 1.0  # multiplier of real samples [0; 1];
# if it's closer to 0, discriminator will struggle to distinguish real and fake samples more

SAVE_STEP = 100

THRESHOLD = 0.7  # threshold of probability while generating a midi file
# GAN generates probabilities that note is on during specific time unit

N_BATCH = 10  # number of batches the dataset is divided into

GLOBAL_SEED = 2137

# physical_devices = tf.config.experimental.list_physical_devices('GPU')
# tf.config.experimental.set_memory_growth(physical_devices[0], True)


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
        data_processed = np.zeros((1, AVG, 128))

        # trim or extend data to shape (AVG x 128)
        if (data_lines.shape[0]) > AVG:
            data_processed[0] = np.delete(
                data_lines, slice(AVG, data_lines.shape[0]), 0)
        else:
            data_processed[0][0:data_lines.shape[0]] = data_lines

        self.data = np.append(self.data, data_processed, axis=0)
        self.data = np.array(self.data, dtype=np.float16)

        # y: 1 - the image is real, 0 - the image is fake
        return data_processed, 1

    def postprocess_array(self, array: np.ndarray) -> np.ndarray:
        if array.shape[1] != 128:
            array = np.swapaxes(array, 0, 1)
        out = (array - np.min(array)) / (np.max(array) - np.min(array))
        out[out < THRESHOLD] = 0
        out *= 255

        return out

    def create_dataset(self, dataset: list[tuple[Any, Any]]) -> tuple[Any, Any]:
        return self.data, np.ones(len(dataset))

    def model_summary(self) -> str:
        return self.model.summary() + self.generator.summary() + self.discriminator.summary()

    def save(self, path: Path) -> None:
        self.save_models(path, self.model, 0)

    def save_npy(self, prediction: np.ndarray, save_path: Path | None, save_name: str) -> None:
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

        print("Model loaded!")

    def define_discriminator(self) -> Sequential:
        model = Sequential()
        start_height = 128 // 8
        start_width = AVG // 8
        filters = 128*AVG // 4

        model.add(Conv1D(64, 3, padding='same', input_shape=(128, AVG)))
        model.add(LeakyReLU(alpha=0.2))

        model.add(Conv1D(32, 3, padding='same'))
        model.add(LeakyReLU(alpha=0.2))

        model.add(Flatten())
        model.add(Dropout(0.4))

        model.add(Activation(activations.gelu))
        opt = Adam(learning_rate=0.0005, beta_1=0.5)
        model.compile(loss='mae', optimizer=opt, metrics=['Accuracy'])

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

        model.add(Conv1DTranspose(filters, 3, strides=2, padding='same'))
        model.add(LeakyReLU(alpha=0.2))

        model.add(Conv1DTranspose(filters, 3, strides=4, padding='same'))
        model.add(LeakyReLU(alpha=0.2))

        model.add(Conv1DTranspose(filters//2, 3, strides=4, padding='same'))
        model.add(LeakyReLU(alpha=0.2))

        model.add(Dropout(0.2))
        model.add(Reshape((128, AVG)))

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
            optimizer = Adam(lr=0.04, beta_1=0.5)
        model.compile(loss=loss, optimizer=optimizer, metrics=['Accuracy'])
        model.add(Flatten())
        print(model.summary())

        return model

    def generate_real_samples(self, dataset: np.ndarray, n_samples: int) -> tuple[Any, Any]:
        ix = np.random.randint(0, len(dataset), n_samples)
        x = np.array(dataset)[ix]
        for i in range(ix.shape[0]):
            x[i] = np.asarray(x[i], dtype=np.float16)

        y = np.ones((n_samples, 1))

        return np.swapaxes(np.asarray(x), 1, 2), y

    def generate_latent_points(self, latent_dim: int, n_samples: int, seed: int) -> np.ndarray:
        rng = np.random.default_rng(seed)
        x_input = rng.integers(2, size=latent_dim * n_samples)
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

    def save_models(self, save_path: Path | None, gan: Sequential, step: int) -> None:
        if save_path is not None:
            save_gan_path = f'{save_path}/gan_models'
            if not os.path.exists(save_gan_path):
                os.makedirs(save_gan_path)
            gan.save(save_gan_path + f'/gan_model' + str(step) + '.h5')

    def train(self, epochs: int, x_train: Any, y_train: Any, progress_callback: ProgressCallback,
              checkpoint_path: Path | None = None) -> None:

        batch_per_epoch = len(x_train) // N_BATCH
        half_batch = N_BATCH // 2
        n_steps = batch_per_epoch * epochs
        history: dict = {'discriminator_real_loss': [],
                         'discriminator_fake_loss': [],
                         'generator_loss': []}

        for step in range(n_steps):
            epoch = step // batch_per_epoch

            x_real, y_real = self.generate_real_samples(self.data, half_batch)
            x_fake, y_fake = self.generate_fake_samples(self.generator, LATENT_DIM, half_batch, GLOBAL_SEED)

            d_loss1 = self.discriminator.train_on_batch(x_real, y_real)
            d_loss2 = self.discriminator.train_on_batch(x_fake, y_fake)

            z_input = self.generate_latent_points(LATENT_DIM, N_BATCH, GLOBAL_SEED)
            y_real2 = np.ones((N_BATCH, 1))
            g_loss = self.model.train_on_batch(z_input, y_real2)

            x, y = self.generate_fake_samples(self.generator, LATENT_DIM, 25, GLOBAL_SEED)

            progress_callback((((d_loss1[0] + d_loss2[0])/2, step), (g_loss[0], step)))

            history['discriminator_real_loss'].append(d_loss1)
            history['discriminator_fake_loss'].append(d_loss2)
            history['generator_loss'].append(g_loss)
            epoch = step // batch_per_epoch + 1

            if step % batch_per_epoch == 0:
                print('epoch: %d, discriminator_real_loss=%.3f, discriminator_fake_loss=%.3f, generator_loss=%.3f \n'
                      % (epoch, d_loss1[0], d_loss2[0], g_loss[0]))

            if step % SAVE_STEP == 0:
                self.save_npy(self.postprocess_array(x_fake[0]), checkpoint_path, str(step))
                self.save_models(checkpoint_path, self.model, step)

    def generate(self, path: Path, seed: int | list[int] | None = None) -> None:
        if (isinstance(seed, int)):
            x_fake, y_fake = self.generate_fake_samples(self.generator, LATENT_DIM, 1, seed)
        else:
            x_fake, y_fake = self.generate_fake_samples(self.generator, LATENT_DIM, 1, GLOBAL_SEED)

        x_array = self.postprocess_array(x_fake[0])
        get_file_from_standard_features(x_array, 500000, path, True, False, False)

    @staticmethod
    def get_progress_metadata() -> ProgressMetadata:
        return ProgressMetadata(x_label='Epoch', y_label='loss', legends=['Discriminator loss', 'Generator loss'])


'''
if __name__ == '__main__':

    g = GAN()
    midi_paths = []
    for dirpath, dirs, files in os.walk(DATA_PATH): 
        for filename in files:
            fname = os.path.join(dirpath,filename)
            if fname.endswith('.mid'):
                midi_paths.append(fname)
    g.train_on_files(midi_paths, 2000, lambda epoch : None, checkpoint_path='xd')
'''
