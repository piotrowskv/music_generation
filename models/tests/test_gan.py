from pathlib import Path

from models.gan.gan_2D import GAN

all_notes = Path('../midi/tests/test_files/test_notes/test_all_notes.mid')
sample_file = Path('../midi/tests/test_files/test_polyphony/test_tempos_velocities_and_polyphony.mid')
one_note = Path('../midi/tests/test_files/test_notes/one_note.mid')


def test_dataset_creating():
    model = GAN()
    model.prepare_data(all_notes)
    assert len(model.data) >= 1


def test_model_loading(tmpdir):

    path = Path(tmpdir)
    path.mkdir(exist_ok=True)
    path = path.joinpath('model')

    model = GAN()
    model.train_on_files([all_notes, sample_file], 1, lambda loss: None)
    model.save(path)
    model2 = GAN()
    model2.load(path)
    assert model.discriminator is not None
    assert model.generator is not None
    assert model.model is not None


def test_model_generating_sample(tmpdir):
    path = Path(tmpdir)
    path.mkdir(exist_ok=True)

    out_file = path.joinpath('sample.mid')

    model = GAN()
    model.train_on_files([all_notes, sample_file], 1, lambda loss: None)
    model.generate(out_file, None)
    assert out_file.exists()


def test_loaded_model_generating_sample(tmpdir):
    path = Path(tmpdir)
    path.mkdir(exist_ok=True)

    model_save = path.joinpath('model')
    out_file = path.joinpath('sample.mid')

    model = GAN()
    model.train_on_files([all_notes, sample_file], 1, lambda loss: None)
    model.save(model_save)
    model2 = GAN()
    model2.load(model_save)
    model2.generate(out_file, None)
    assert out_file.exists()
