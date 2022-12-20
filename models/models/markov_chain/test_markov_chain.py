import markov_chain
import pytest
import os

#path = "models\\models\\markov_chain\\test_files"

one_note = ['test_files/test_one_note.mid']
all_notes = ['test_files/test_all_notes.mid']
sample_file = ['test_files/test_tempos_velocities_and_polyphony.mid']

def test_data_loading():
    model = markov_chain.MarkovChain()
    model.train_on_files(all_notes, 10, lambda epoch, loss : None)
    print(len(model.tokens))

def test_not_empty():
    model = markov_chain.MarkovChain()
    model.train_on_files(all_notes, 10, lambda epoch, loss : None)
    assert len(model.data)>0
    assert len(model.probabilities) >0
    assert len(model.tokens) >0

def test_one_token():
    model = markov_chain.MarkovChain()
    model.train_on_files(one_note, 10, lambda epoch, loss : None)
    assert len(model.tokens) == 1

def test_multiple_tokens():
    model = markov_chain.MarkovChain()
    model.train_on_files(all_notes, 10, lambda epoch, loss : None)
    assert len(model.tokens) ==128

def test_probabilities_all_notes1():
    model = markov_chain.MarkovChain()
    model.train_on_files(all_notes, 10, lambda epoch, loss : None)
    assert len(model.probabilities[0]) == 1

def test_probabilities_all_notes2():
    model = markov_chain.MarkovChain()
    model.train_on_files(all_notes, 10, lambda epoch, loss : None)
    assert model.probabilities[0][(97,)] == 1.0

def test_probabilities_one_note1():
    model = markov_chain.MarkovChain()
    model.train_on_files(one_note, 10, lambda epoch, loss : None)
    assert len(model.probabilities[0]) == 1

def test_probabilities_one_note2():
    model = markov_chain.MarkovChain()
    model.train_on_files(one_note, 10, lambda epoch, loss : None)
    assert model.probabilities[0][(72,)] == 1

def test_multiple_tracks():
    model = markov_chain.MarkovChain()
    model.train_on_files(sample_file, 10, lambda epoch, loss : None)
    assert len(model.data) > 1

test_data_loading()
test_not_empty()
test_one_token()
test_multiple_tokens()
test_probabilities_all_notes1()
test_probabilities_all_notes2()
test_probabilities_one_note1()
test_probabilities_one_note2()
test_multiple_tracks()