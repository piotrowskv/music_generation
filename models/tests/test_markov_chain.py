from pathlib import Path
import os

from models.markov_chain.markov_chain import MarkovChain

all_notes = ['../midi/tests/test_files/test_notes/test_all_notes.mid']
sample_file = [
    '../midi/tests/test_files/test_polyphony/test_tempos_velocities_and_polyphony.mid']
one_note = ['../midi/tests/test_files/test_notes/one_note.mid']


def test_data_loading():
    model = MarkovChain()
    model.train_on_files(all_notes, 0, lambda epoch: None)
    assert len(model.data) > 0


def test_token_creation_after_loading():
    model = MarkovChain()
    model.train_on_files(all_notes, 0, lambda epoch: None)
    assert len(model.tokens) > 0


def test_probabilities_after_loading():
    model = MarkovChain()
    model.train_on_files(all_notes, 0, lambda epoch: None)
    assert len(model.probabilities) > 0


def test_multiple_tokens_creating():
    model = MarkovChain()
    model.train_on_files(all_notes, 0, lambda epoch: None)
    assert len(model.tokens) == 128


def test_multiple_tokens_probabilities():
    model = MarkovChain()
    model.train_on_files(all_notes, 0, lambda epoch: None)
    assert len(model.probabilities) == 128


def test_multiple_tokens_probabilities_values():
    model = MarkovChain()
    model.train_on_files(all_notes, 0, lambda epoch: None)
    assert model.probabilities[(121, )] == {(54, ): 0.75, (55, ): 0.25}


def test_multiple_tracks():
    model = MarkovChain()
    model.train_on_files(sample_file, 0, lambda epoch: None)
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

    assert len(model2.probabilities) > 0


def test_loaded_model_generate(tmpdir):
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir, exist_ok=True)

    path = Path(tmpdir).joinpath('markov_saved.npz')

    model = MarkovChain()
    model.train_on_files(all_notes, 10, lambda epoch: None)
    model.save(path)
    model2 = MarkovChain()
    model2.load(path)
    res = model2.predict(model2.tokens_list[0], 100, False, 0, None, tmpdir)
    assert res.shape == (100, 128)
