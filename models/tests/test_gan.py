from pathlib import Path
import os
import time

from models.gan.gan_2D import GAN

all_notes = '../midi/tests/test_files/test_notes/test_all_notes.mid'
sample_file = '../midi/tests/test_files/test_polyphony/test_tempos_velocities_and_polyphony.mid'
one_note = '../midi/tests/test_files/test_notes/one_note.mid'


def test_dataset_creating():
    model = GAN()
    model.prepare_data(all_notes)
    assert len(model.data) >= 1


def test_model_loading(tmpdir):
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir, exist_ok=True)

    model = GAN()
    model.train_on_files([all_notes, sample_file], 1, lambda loss: None)
    model.save(tmpdir)
    model2 = GAN()
    model2.load(tmpdir)
    assert model.discriminator is not None
    assert model.generator is not None
    assert model.model is not None


def test_model_generating_sample(tmpdir):
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir, exist_ok=True)

    model = GAN()
    model.train_on_files([all_notes, sample_file], 1, lambda loss: None)
    model.generate(tmpdir + "/sample.mid", None)
    assert os.path.exists(tmpdir + "/sample.mid")


def test_loaded_model_generating_sample(tmpdir):
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir, exist_ok=True)

    model = GAN()
    model.train_on_files([all_notes, sample_file], 1, lambda loss: None)
    model.save(tmpdir)
    model2 = GAN()
    model2.load(tmpdir)
    model2.generate(tmpdir + "/sample.mid", None)
    assert os.path.exists(tmpdir + "/sample.mid")
