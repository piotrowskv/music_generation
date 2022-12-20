import pytest

from midi.music_21 import check_number_of_tracks


def test_check_number_of_tracks_correct():
    check_number_of_tracks([1, 2, 3, 4, 5, 6], 'filename', 6)


def test_check_number_of_tracks_incorrect():
    with pytest.raises(ValueError):
        check_number_of_tracks([1, 2, 3], 'filename', 4)
