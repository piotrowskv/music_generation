from models.gan.gan_2D import GAN

def test_gan_loads_data():
    files = ['midi/tests/test_files/test_encoder/test_2d_array.mid']
    gan = GAN()
    g.create_dataset(files)
    assert len(gan.data)>0
    assert gan.data[0].shape == (512, 128)

def test_load_gan_model():
    files = 'testing_gan.h5'
    gan = GAN()
    gan.define_gan()
    gan.save(files)
    gan2 = GAN()
    gan2.load(files)
    assert gan2.generator is not None
    assert gan2.discriminator is not None
    assert gan2.model is not None