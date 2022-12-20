import pytest
from midi.decode import *

# get_sequence_of_notes(path, False, False, True)midi\tests\test_files\test_all_notes\SBFT.npy
# fft stands for False, False, True
def test_get_sequence_of_notes_fft_range(filepath):  # path to tested .mid file
    array = np.load(path_notes + '\\SBFT.npy', allow_pickle=True)

    with pytest.raises(AssertionError):
        out_array = get_sequence_of_notes(filepath, False, False, True)

    assert array == out_array

def test_get_sequence_of_notes_fff_range(filepath):  # path to tested .mid file
    array = np.load(path_notes + '\\SBFF.npy', allow_pickle=True)

    with pytest.raises(AssertionError):
        out_array = get_sequence_of_notes(filepath, False, False, False)

    assert array == out_array

def test_get_sequence_of_notes_ftf_range(filepath):  # path to tested .mid file
    array = np.load(path_notes + '\\SBTF.npy', allow_pickle=True)

    with pytest.raises(AssertionError):
        out_array = get_sequence_of_notes(filepath, False, True, False)

    assert array == out_array

def test_get_sequence_of_notes_ftt_range(filepath):  # path to tested .mid file
    array = np.load(path_notes + '\\SBTT.npy', allow_pickle=True)

    with pytest.raises(AssertionError):
        out_array = get_sequence_of_notes(filepath, False, True, True)

    assert array == out_array

def test_get_sequence_of_notes_tft_range(filepath):  # path to tested .mid file
    array = np.load(path_notes + '\\SVFT.npy', allow_pickle=True)

    with pytest.raises(AssertionError):
        out_array = get_sequence_of_notes(filepath, False, False, True)

    assert array == out_array

def test_get_sequence_of_notes_tff_range(filepath):  # path to tested .mid file
    array = np.load(path_notes + '\\SVFF.npy', allow_pickle=True)

    with pytest.raises(AssertionError):
        out_array = get_sequence_of_notes(filepath, False, False, False)

    assert array == out_array

def test_get_sequence_of_notes_ttf_range(filepath):  # path to tested .mid file
    array = np.load(path_notes + '\\SVTF.npy', allow_pickle=True)

    with pytest.raises(AssertionError):
        out_array = get_sequence_of_notes(filepath, False, True, False)

    assert array == out_array

def test_get_sequence_of_notes_ttt_range(filepath):  # path to tested .mid file
    array = np.load(path_notes + '\\SVTT.npy', allow_pickle=True)

    with pytest.raises(AssertionError):
        out_array = get_sequence_of_notes(filepath, False, True, True)

    assert array == out_array

def test_get_array_of_notes_tt_range(filepath):  # path to tested .mid file
    array = np.load(path_notes + '\\AVT.npy', allow_pickle=True)

    with pytest.raises(AssertionError):
        out_array = get_array_of_notes(filepath, True, True)

    assert array == out_array

def test_get_array_of_notes_tf_range(filepath):  # path to tested .mid file
    array = np.load(path_notes + '\\AVF.npy', allow_pickle=True)

    with pytest.raises(AssertionError):
        out_array = get_sequence_of_notes(filepath, True, False)

    assert array == out_array

def test_get_array_of_notes_ft_range(filepath):  # path to tested .mid file
    array = np.load(path_notes + '\\ABT.npy', allow_pickle=True)

    with pytest.raises(AssertionError):
        out_array = get_sequence_of_notes(filepath, False, True)

    assert array == out_array

def test_get_array_of_notes_tt_range(filepath):  # path to tested .mid file
    array = np.load(path_notes + '\\ABF.npy', allow_pickle=True)

    with pytest.raises(AssertionError):
        out_array = get_sequence_of_notes(filepath, False, False)

    assert array == out_array


def test_all(filepath):
    test_get_sequence_of_notes_fft_range(file_path)
    test_get_sequence_of_notes_fff_range(file_path)
    test_get_sequence_of_notes_ftt_range(file_path)
    test_get_sequence_of_notes_ftf_range(file_path)

    test_get_sequence_of_notes_tft_range(file_path)
    test_get_sequence_of_notes_tff_range(file_path)
    test_get_sequence_of_notes_ttt_range(file_path)
    test_get_sequence_of_notes_ttf_range(file_path)

    test_get_array_of_notes_ft_range(file_path)
    test_get_array_of_notes_ff_range(file_path)
    test_get_array_of_notes_tt_range(file_path)
    test_get_array_of_notes_tf_range(file_path)

if __name__ == '__main__':
    path_notes = 'test_files\\test_all_notes'
    file_path = path_notes + '\\test_all_notes.mid'
    test_all(file_path)
    
    path_notes = 'test_files\\test_tempos_etc'
    file_path = path_notes + '\\test_tempos_etc.mid'
    test_all(file_path)

# def test_get_sequence_of_notes_fft_tempos_velocities_polyphony():
# same, but the second file