import os
import unittest
import numpy as np

from mido import MidiTrack, MidiFile
from mido.messages import Message

from midi.midi_decode import *
from midi.midi_encode import *


class TestMidiDecodeClassesFunctions(unittest.TestCase):
    def test_SeparateNote_init(self):
        pass

    def test_SeparateNote_normalise(self):
        pass

    def test_EventNote_init(self):
        pass

    def test_EventNote_normalise(self):
        pass

    def test_ActiveElement_init(self):
        pass

    def test_Event_init_booleans_mode(self):
        pass

    def test_Event_init_velocities_mode(self):
        pass

    def test_Event_init_notes_mode(self):
        pass

    def test_Event_set_notes_array(self):
        pass

    def test_Event_normalise(self):
        pass


class TestMidiDecodeSeparateFunctions(unittest.TestCase):
    def test_get_offset(self):
        pass

    def test_get_midi_length(self):
        pass

    def test_check_file_type_0_correct(self):
        pass
        # create midi file type 0

    def test_check_file_type_1_correct(self):
        pass
        # create midi file type 1

    def test_check_file_type_1_incorrect(self):  # TODO: should test track amount > 0, raise error
        pass
        # create midi file type 1

    def test_check_file_type_2(self):
        # create midi file type 2
        self.assertRaises(ValueError)

    def test_get_filename_correct(self):
        self.assertEqual()

    def test_get_filename_incorrect(self):
        self.assertRaises(ValueError)

    def test_get_tempo_array(self):
        pass

    def test_export_output(self):
        # create numpy array
        pass
        # delete afterwards

    def test_combine_and_clean_tracks_single(self):
        # create single track midi file
        pass

    def test_combine_and_clean_tracks_multi(self):
        # create multitrack midi file
        pass

    def test_get_max_velocity(self):
        pass


class TestMidiDecodeCompositeFunctions(unittest.TestCase):
    def test_export_tempo_array(self):
        pass

    def test_open_file_standard(self):
        pass

    def test_open_file_modified(self):
        # create an unusual PPQ file
        pass

    def test_prepare_file_with_join(self):
        pass

    def test_prepare_file_without_join(self):
        pass

    def test_get_lists_of_events_booleans_mode(self):
        pass

    def test_get_lists_of_events_velocities_mode(self):
        pass

    def test_get_lists_of_events_notes_mode(self):
        pass

    def test_initialise_sequences(self):
        pass

    def test_get_sequence_of_notes(self):
        # MULTIPLE TESTS
        pass

    def test_get_array_of_notes(self):
        # MULTIPLE TESTS
        pass


class TestMidiEncode(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
