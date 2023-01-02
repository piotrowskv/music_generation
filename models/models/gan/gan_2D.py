from pathlib import Path
import os
import glob
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from typing import Any, Callable
from keras.callbacks import Callback, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Reshape, Flatten, Dropout, LeakyReLU, Conv1D, Conv1DTranspose, Activation
from tensorflow.keras import activations
from models.music_model import MusicModel
from midi.decode import get_array_of_notes
from midi.encode import get_file_from_standard_features



DATA_PATH = 'data'

AVG = 512 # length of generated array 

LATENT_DIM = 512 # dimension of latent space
# higher LATNT_DIM -> samples produced by generator converge more to dataset


REAL_MULTIPLIER = 1.0 # multiplier of real sampls [0;1];
# if it's closer to 0, discriminator will struggle to distiguish real and fake samples more

SAVE_STEP = 100

TRESHOLD = 0.7 # treshold of probability while generating a midi file
# GAN generates probabilities that note is on during specific time unit

N_BATCH = 10 # number of batches the dataset is divided into

#physical_devices = tf.config.experimental.list_physical_devices('GPU')
#tf.config.experimental.set_memory_growth(physical_devices[0], True)

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
        data_lines = get_array_of_notes(midi_file, False, False)
        for i in range(len(data_lines)): #serialize tracks
            assert data_lines[i].shape[1]==128, "Incorrct number of notes (expected: 128)"
            data_processed = np.zeros((1, AVG, 128))
            #trim or extend data to shape (AVG x 128)
            if((data_lines[i].shape[0])> AVG):
                data_processed[0] = np.delete(data_lines[i], slice(AVG, data_lines[i].shape[0]),0)
            else:
                data_processed[0][0:data_lines[i].shape[0]] = data_lines[i]

            self.data = np.append(self.data, data_processed, axis=0)
        
        self.data = np.array(self.data, dtype=np.float16)

        # y: 1 - the image is real, 0 - the image is fake
        return data_processed, 1

    def postprocess_array(self, array: np.ndarray) -> np.ndarray:
        if(array.shape[1]!=128):
            array = np.swapaxes(array, 0, 1)
        out =  (array - np.min(array)) / (np.max(array) - np.min(array))
        out[out<TRESHOLD] = 0
        out*=255
        return out

    def create_dataset(self, dataset: list[tuple[Any, Any]]) -> tuple[Any, Any]:
        return self.data, np.ones(len(dataset))

    def model_summary(self) -> str:
        return self.model.summary() + self.generator.summary() + self.discriminator.summary()

    def save(self, path: Path) -> None:
        self.save_models(path, self.model, 0)

    def save_npy(self, prediction: np.ndarray, save_path: Path | None, save_name: str) -> None:
        if(save_path is not None):
            os.makedirs(save_path, exist_ok=True)
            np.save('{}/{}'.format(save_path, save_name), prediction)

    def load(self, path: Path) -> None:
        # path to GAN defined exactly like in define_gan
        self.model = load_model(path)
        assert len(self.model.layers)==3 and self.model.layers[0].name =='sequential_1' and self.model.layers[1].name =='sequential', "Incorrect model."

        self.generator = self.model.get_layer('sequential')
        self.discriminator = self.model.get_layer('sequential_1')
        print("Model loaded!")

    def define_discriminator(self) -> Sequential:
        model = Sequential()
        start_height = 128 // 8
        start_width = AVG // 8
        filters = 128*AVG //4

        model.add(Conv1D(filters, 3, padding='same', input_shape=(128,AVG)))
        model.add(LeakyReLU(alpha=0.2))

        model.add(Conv1D(64, 3, strides=2, padding='same'))
        model.add(LeakyReLU(alpha=0.2))

        model.add(Conv1D(64, 3, strides=2, padding='same'))
        model.add(LeakyReLU(alpha=0.2))

        model.add(Flatten())
        model.add(Dropout(0.4))
        model.add(Activation(activations.gelu))
        opt = Adam(lr=0.04, beta_1=0.5)
        model.compile(loss='mae', optimizer=opt, metrics=['Accuracy'])
        print(model.summary())
        return model

    def define_generator(self, latent_dim: int) -> Sequential:
        start_height = 128 // 8
        start_width = AVG // 8
        filters = AVG*2
        model = Sequential()

        n_nodes = start_width * start_height
        model.add(Dense(n_nodes, input_dim=latent_dim))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Reshape((32, 32)))

        model.add(Conv1DTranspose(64, 3, strides=2, padding='same'))
        model.add(LeakyReLU(alpha=0.2))

        model.add(Conv1DTranspose(64, 3, padding='same'))
        model.add(LeakyReLU(alpha=0.2))
        
        model.add(Conv1DTranspose(filters, 3, padding='same'))
        model.add(LeakyReLU(alpha=0.2))

        model.add(Dropout(0.2))
        model.add(Reshape((128, AVG)))
        print(model.summary())
        return model

    def define_gan(self, g_model: Sequential, d_model: Sequential, loss:str ='binary_crossentropy', optimizer: Any =None) -> Sequential:
        d_model.trainable = False
        model = Sequential()
        model.add(g_model)
        model.add(d_model)
        if not optimizer:
            optimizer = Adam(lr=0.04, beta_1=0.5)
        model.compile(loss=loss, optimizer=optimizer, metrics=['Accuracy'])
        model.add(Flatten())
        print(model.summary())
        return model

    def generate_real_samples(self, dataset: np.ndarray, n_samples: int) -> tuple[Any, Any]:
        ix = np.random.randint(0, len(dataset), n_samples)
        X = np.array(dataset)[ix]
        for i in range(ix.shape[0]):
           X[i]=np.asarray(X[i], dtype=np.float16)

        y = np.ones((n_samples, 1))
        return np.swapaxes(np.asarray(X), 1, 2), y

    def generate_latent_points(self, latent_dim: int, n_samples:int) -> np.ndarray:
        x_input = np.random.randn(latent_dim * n_samples)
        x_input = x_input.reshape(n_samples, latent_dim)
        return x_input

    def generate_fake_samples(self, generator: Sequential, latent_dim: int, n_samples: int) -> tuple[np.ndarray, np.ndarray]:
        x_input = self.generate_latent_points(latent_dim, n_samples)
        X = generator.predict(x_input)
        y = np.zeros((n_samples, 1)) 
        return X, y

    def save_models(self, save_path: Path | None, gan: Sequential, step: int) -> None:
        if(save_path is not None):
            save_gan_path = f'{save_path}/gan_models'
            if not os.path.exists(save_gan_path):
                os.makedirs(save_gan_path)
            gan.save(save_gan_path + f'/gan_model' +str(step) + '.h5')

    def train(self, epochs: int, xtrain: Any, ytrain: Any, loss_callback: Callback, checkpoint_path: Path | None = None) -> None:
        latent_dim = LATENT_DIM
        real_samples_multiplier= REAL_MULTIPLIER 
        n_batch = N_BATCH
        print(n_batch)
        save_step = SAVE_STEP
        batch_per_epoch = len(xtrain)// n_batch
        print(batch_per_epoch)
        half_batch = n_batch // 2
        seed = self.generate_latent_points(latent_dim, 128)
        n_steps = batch_per_epoch * epochs
        history : dict = {'discriminator_real_loss': [],
                'discriminator_fake_loss': [],
                'generator_loss': []}
        for step in range(n_steps):
            epoch = step // batch_per_epoch
            disc_loss_real = 0.0
            disc_loss_fake = 0.0
            disc_accuracy = 0.0
            for disc_batch in range(n_batch):
                X_real, y_real = self.generate_real_samples(xtrain, half_batch)
                disc_data_real =  self.discriminator.train_on_batch(X_real, y_real)
                disc_loss_real += disc_data_real[0]
                X_fake, y_fake = self.generate_fake_samples(self.generator, latent_dim, half_batch)
                disc_data_fake = self.discriminator.train_on_batch(X_fake, y_fake)
                disc_loss_fake += disc_data_fake[0]
            disc_loss_real /= n_batch
            disc_loss_fake /= n_batch
            disc_accuracy = (disc_data_real[1] + disc_data_fake[1])/2
            X_gan = self.generate_latent_points(latent_dim, n_batch)
            y_gan = np.zeros((n_batch, 1)) * real_samples_multiplier
            g_data = self.model.train_on_batch(X_gan, y_gan)
            g_loss= g_data[0]
            
            history['discriminator_real_loss'].append(disc_loss_real)
            history['discriminator_fake_loss'].append(disc_loss_fake)
            history['generator_loss'].append(g_loss)
            epoch = step // batch_per_epoch+1
            if step%batch_per_epoch==0:
                print('epoch: %d, discriminator_real_loss=%.3f, discriminator_fake_loss=%.3f, generator_loss=%.3f \n discriminator_accuracy = %.3f, GAN_accuracy = %.3f' % (epoch, disc_loss_real, disc_loss_fake, g_loss, disc_accuracy, g_data[1]))
            if step%save_step==0:
                self.save_npy(self.postprocess_array(X_fake[0]), checkpoint_path, str(step))
                self.save_models(checkpoint_path, self.model, step)

    def generate(self, path: Path, seed: int | list[int] | None = None) -> None:
        if seed is None:
            X_fake, y_fake = self.generate_fake_samples(self.generator, LATENT_DIM, 1)
        else:
            X_fake, y_fake = self.generate_fake_samples(self.generator, LATENT_DIM, 1)
            
        X_array = self.postprocess_array(X_fake[0])
        get_file_from_standard_features(X_array, 500000, path, True, False, False)




if __name__ == '__main__':
    '''
    g = GAN()
    midi_paths = []
    for dirpath, dirs, files in os.walk(DATA_PATH): 
        for filename in files:
            fname = os.path.join(dirpath,filename)
            if fname.endswith('.mid'):
                midi_paths.append(fname)
    print(len(g.data))
    g.train_on_files(midi_paths, 16, lambda epoch, loss : None, checkpoint_path='idk')
    '''
