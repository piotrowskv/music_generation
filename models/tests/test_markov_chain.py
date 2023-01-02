from models.markov_chain.markov_chain import MarkovChain


def test_generate_n_grams():
    model = MarkovChain()

    model.data = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 0]]
    model.generate_n_grams(3)

    assert model.n_grams_list == list(set([
        (1, 2, 3), (2, 3, 4), (3, 4, 5), (6, 7, 8), (7, 8, 9), (8, 9, 0)]))
