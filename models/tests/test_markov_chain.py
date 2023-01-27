from pathlib import Path
import os

from models.markov_chain.markov_chain import MarkovChain

all_notes = ['../midi/tests/test_files/test_notes/test_all_notes.mid']
sample_file = [
    '../midi/tests/test_files/test_polyphony/test_tempos_velocities_and_polyphony.mid']
one_note = ['../midi/tests/test_files/test_notes/one_note.mid']


def test_data_loading():
    model = MarkovChain()
    model.train_on_files(all_notes, 10, lambda epoch: None)

    assert len(model.data) > 0
    assert len(model.probabilities) > 0
    assert len(model.tokens) > 0


def test_multiple_tokens():
    model = MarkovChain()
    model.train_on_files(all_notes, 10, lambda epoch: None)

    assert len(model.tokens) == 128


def test_multiple_tracks():
    model = MarkovChain()
    model.train_on_files(sample_file, 10, lambda epoch: None)

    assert len(model.data) > 1


def test_model_saving_and_loading(tmpdir):

    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir, exist_ok=True)

    path = Path(tmpdir).joinpath('markov_saved.npz')

    model = MarkovChain()
    model.train_on_files(sample_file, 10, lambda epoch: None)
    model.save(path)
    model2 = MarkovChain()
    model2.load(path)

    assert len(model.probabilities) > 0
