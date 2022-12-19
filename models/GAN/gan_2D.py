
import glob
import os
import tensorflow as tf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Reshape
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import LeakyReLU
from tensorflow.keras.layers import Conv1D
from tensorflow.keras.layers import Conv1DTranspose
from tensorflow.keras.layers import Activation
from tensorflow.keras import activations

DATA_PATH = 'data/sequences'
#AVG = 11647
AVG = 512
class GAN(Sequential):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def data_preprocessing(self, DATA_PATH):
        print("Data loading...")
        data_lines = []
        data = []
        sum_x = 0
        min_ = 20000
        for filename in os.listdir(DATA_PATH):
            data_lines.append(np.load(os.path.join(DATA_PATH, filename)))

        for i in range(len(data_lines)):
            for j in range(data_lines[i].shape[0]):
                data.append(data_lines[i][j].tolist())


        dataset = data
        notes = np.zeros((len(data), 128, AVG))
        zeros = np.zeros((1, 128))

        for i in range(len(dataset)):
            dataset[i]=np.array(dataset[i])
            if dataset[i].shape[0] > AVG:
                dataset[i] = np.delete(dataset[i], slice(AVG, dataset[i].shape[0]),0)


        for i in range(len(dataset)):
            notes[i] = np.swapaxes(dataset[i],0,1)

        print(np.array(dataset).shape)
        return dataset, notes

    def save_npy(self, prediction, save_path, save_name):
        os.makedirs(save_path, exist_ok=True)
        np.save('{}/{}'.format(save_path, save_name), prediction)

    
    def define_discriminator(self):
        model = Sequential()
        start_height = 128 // 8
        start_width = AVG // 8
        filters = 128*AVG //4

        model.add(Conv1D(filters, 3, padding='same', input_shape=(128,AVG)))
        model.add(LeakyReLU(alpha=0.2))

        model.add(Conv1D(128, 3, strides=2, padding='same'))
        model.add(LeakyReLU(alpha=0.2))

        #model.add(Conv1D(128, 3, strides=2, padding='same'))
        #model.add(LeakyReLU(alpha=0.2))

        #model.add(Conv1D(256, 3, strides=2, padding='same'))   
        #model.add(LeakyReLU(alpha=0.2))

        model.add(Flatten())
        model.add(Dropout(0.4))
        model.add(Activation(activations.gelu))
        opt = Adam(lr=0.04, beta_1=0.5)
        model.compile(loss='mae', optimizer=opt, metrics=['Accuracy'])
        print(model.summary())
        return model

    def define_generator(self, latent_dim):
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
        #model.add(Reshape((8*start_height, 256)))
        
        model.add(Conv1DTranspose(filters, 3, padding='same'))
        model.add(LeakyReLU(alpha=0.2))
        
        #model.add(Conv1DTranspose(128, 4, strides=3, padding='same'))
        #model.add(LeakyReLU(alpha=0.2))

        model.add(Dropout(0.2))
        #model.add(Conv1D(81, 3, activation='tanh', padding='same'))
        model.add(Reshape((128,AVG)))
        print(model.summary())
        return model

    def define_gan(self, g_model, d_model, loss='binary_crossentropy', optimizer=None):
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

    def generate_real_samples(self, dataset, n_samples):
        ix = np.random.randint(0, len(dataset), n_samples)
        X = np.array(dataset)[ix]
        for i in range(ix.shape[0]):
            X[i]=np.asarray(X[i], dtype=np.float32)

        y = np.ones((n_samples, 1))
        return X, y

    def generate_latent_points(self, latent_dim, n_samples):
        x_input = np.random.randn(latent_dim * n_samples)
        x_input = x_input.reshape(n_samples, latent_dim)
        return x_input

    def generate_fake_samples(self, generator, latent_dim, n_samples):
        x_input = self.generate_latent_points(latent_dim, n_samples)
        X = generator.predict(x_input)
        y = np.ones((n_samples, 1)) 
        return X, y

    def save_models(self, save_path, generator, discriminator, gan, step):
        save_generator_path = f'{save_path}/generator_models'
        save_discriminator_path = f'{save_path}/discriminator_models'
        save_gan_path = f'{save_path}/gan_models'
        if not os.path.exists(save_generator_path):
            os.makedirs(save_generator_path)
        if not os.path.exists(save_discriminator_path):
            os.makedirs(save_discriminator_path)
        if not os.path.exists(save_gan_path):
            os.makedirs(save_gan_path)
        generator.save(save_generator_path + f'/generator_model' + str(step) + '.h5')
        discriminator.save(save_discriminator_path + f'/discriminator_model' + str(step)+'.h5')
        gan.save(save_gan_path + f'/gan_model' +str(step) + '.h5')

    def train(self, generator, discriminator, gan_model, dataset, latent_dim, data,
          real_samples_multiplier=0.8, fake_samples_multiplier=0.0, discriminator_batches=2,
          n_epochs=500, n_batch=128, save_step=1000, save_path="samples"):

        batch_per_epoch = len(dataset)// n_batch
        half_batch = n_batch // 2
        seed = self.generate_latent_points(latent_dim, 128)
        n_steps = batch_per_epoch * n_epochs
        history = {'discriminator_real_loss': [],
                'discriminator_fake_loss': [],
                'generator_loss': []}
        for step in range(n_steps):
            epoch = step // batch_per_epoch
            disc_loss_real = 0.0
            disc_loss_fake = 0.0
            disc_accuracy = 0.0
            for disc_batch in range(discriminator_batches):
                X_real, y_real = self.generate_real_samples(dataset, half_batch)
                disc_data_real =  discriminator.train_on_batch(X_real, y_real)
                disc_loss_real += disc_data_real[0]
                X_fake, y_fake = self.generate_fake_samples(generator, latent_dim, half_batch)
                disc_data_fake = discriminator.train_on_batch(X_fake, y_fake)
                disc_loss_fake += disc_data_fake[0]
            disc_loss_real /= discriminator_batches
            disc_loss_fake /= discriminator_batches
            disc_accuracy = (disc_data_real[1] + disc_data_fake[1])/2
            X_gan = self.generate_latent_points(latent_dim, n_batch)
            y_gan = np.ones((n_batch, 1)) * real_samples_multiplier
            g_data = gan_model.train_on_batch(X_gan, y_gan)
            g_loss= g_data[0]
            
            history['discriminator_real_loss'].append(disc_loss_real)
            history['discriminator_fake_loss'].append(disc_loss_fake)
            history['generator_loss'].append(g_loss)
            epoch = step // batch_per_epoch+1
            if step%batch_per_epoch==0:
                print('epoch: %d, discriminator_real_loss=%.3f, discriminator_fake_loss=%.3f, generator_loss=%.3f \n discriminator_accuracy = %.3f, GAN_accuracy = %.3f' % (epoch, disc_loss_real, disc_loss_fake, g_loss, disc_accuracy, g_data[1]))
            if step%save_step==0:
                self.save_npy(X_fake[0], save_path, step)
                self.save_models(save_path, generator, discriminator, gan_model, step)
                
        return history, gan_model, generator, discriminator
    
    def run(self, data_path, output_length=AVG,   loss='binary_crossentropy', optimizer=None,latent_dim=16, real_samples_multiplier=1.0, fake_samples_multiplier=0.0, discriminator_batches=16, n_epochs=100, n_batch=32, save_step=25, save_path='saved_v6'):
        dataset, notes = self.data_preprocessing(data_path)
        dis = self.define_discriminator()
        gen = self.define_generator(latent_dim)
        gan = self.define_gan(gen, dis,  loss=loss, optimizer=optimizer)
        hist, final_gan, final_generator, final_discriminator = self.train(gen, dis, gan, notes, latent_dim, dataset, real_samples_multiplier=real_samples_multiplier, fake_samples_multiplier=fake_samples_multiplier, discriminator_batches=discriminator_batches, n_epochs=n_epochs, n_batch=n_batch, save_step=save_step, save_path=save_path)
        self.save_models(save_path, final_generator, final_discriminator, final_gan, 'final')
        return hist, final_gan

g = GAN()
g.run(DATA_PATH)
