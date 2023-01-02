from models.markov_chain.markov_chain import MarkovChain

all_notes = ['../midi/tests/test_files/test_notes/test_all_notes.mid']
sample_file = ['../midi/tests/test_files/test_polyphony/test_tempos_velocities_and_polyphony.mid']
one_note = ['../midi/tests/test_files/test_notes/one_note.mid']

markov_saved = 'markov_saved.npy'

def test_generate_n_grams():
    model = MarkovChain()

    model.data = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 0]]
    model.generate_n_grams(3)

    assert model.n_grams_list == list(set([
        (1, 2, 3), (2, 3, 4), (3, 4, 5), (6, 7, 8), (7, 8, 9), (8, 9, 0)]))

def test_data_loading():
    model = MarkovChain()
    print(all_notes)
    model.train_on_files(all_notes, 10, lambda epoch, loss : None)
    assert len(model.data)>0
    assert len(model.probabilities) >0
    assert len(model.tokens) >0

def test_multiple_tokens():
    model = MarkovChain()
    model.train_on_files(all_notes, 10, lambda epoch, loss : None)
    assert len(model.tokens) ==128

def test_probabilities_all_notes1():
    model = MarkovChain()
    model.train_on_files(all_notes, 10, lambda epoch, loss : None)
    assert len(model.probabilities[0]) == 1

def test_probabilities_all_notes2():
    model = MarkovChain()
    model.train_on_files(all_notes, 10, lambda epoch, loss : None)
    print(model.data)
    assert model.probabilities[0][(97,)] == 1.0

def test_multiple_tracks():
    model = MarkovChain()
    model.train_on_files(sample_file, 10, lambda epoch, loss : None)
    assert len(model.data) > 1

def test_model_saving_and_loading():
    model = MarkovChain()
    model.train_on_files(sample_file, 10, lambda epoch, loss : None)
    model.save(markov_saved)
    model2 = MarkovChain()
    model2.load(markov_saved)
    assert len(model.probabilities) > 0
