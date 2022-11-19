#### get_sequence_of_notes(`str` filepath, `Mode` mode, `bool` join_tracks *= False*, `bool` only_active_notes *= True*):

    get_sequence_of_notes(str, Mode.BOOLEANS, False, True)     -> <list> 'tracks' (<list> 'events' (<tuple> (<int> 'time offset', <list> 'active notes')))
    get_sequence_of_notes(str, Mode.BOOLEANS, False, False)    -> <list> 'tracks' (<list> 'events' (<tuple> (<int> 'time offset', <list> (<list [bool], size: 128>))))
    get_sequence_of_notes(str, Mode.BOOLEANS, True, True)      ->                  <list> 'events' (<tuple> (<int> 'time offset', <list> 'active notes'))
    get_sequence_of_notes(str, Mode.BOOLEANS, True, False)     ->                  <list> 'events' (<tuple> (<int> 'time offset', <list> (<list [bool], size: 128>)))

    get_sequence_of_notes(str, Mode.VELOCITIES, False, True)   -> <list> 'tracks' (<list> 'events' (<tuple> (<int> 'time offset', <list> (<tuple> (<int> 'note height', <float> 'note velocity')))))
    get_sequence_of_notes(str, Mode.VELOCITIES, False, False)  -> <list> 'tracks' (<list> 'events' (<tuple> (<int> 'time offset', <list> (<list [float], size: 128>))))
    get_sequence_of_notes(str, Mode.VELOCITIES, True, True)    ->                  <list> 'events' (<tuple> (<int> 'time offset', <list> (<tuple> (<int> 'note height', <float> 'note velocity'))))
    get_sequence_of_notes(str, Mode.VELOCITIES, True, False)   ->                  <list> 'events' (<tuple> (<int> 'time offset', <list> (<list [float], size: 128>)))

    get_sequence_of_notes(str, Mode.NOTES, False, True)        -> <list> 'tracks' (<list> 'events' (<tuple> (<int> 'time offset', <list> (<tuple> (<int> 'note height', <EventNote>)))))
    get_sequence_of_notes(str, Mode.NOTES, False, False)       -> <list> 'tracks' (<list> 'events' (<tuple> (<int> 'time offset', <list> (<list [None | SeparateNote], size: 128>))))
    get_sequence_of_notes(str, Mode.NOTES, True, True)         ->                  <list> 'events' (<tuple> (<int> 'time offset', <list> (<tuple> (<int> 'note height', <EventNote>))))
    get_sequence_of_notes(str, Mode.NOTES, True, False)        ->                  <list> 'events' (<tuple> (<int> 'time offset', <list> (<list [None | SeparateNote], size: 128>)))

#### get_array_of_notes(`str` filepath, `Mode` mode, `bool` join_tracks *= False*):

    get_array_of_notes(str, Mode.BOOLEANS, False)    -> <np.ndarray [bool],                size: 'tracks' x 'grid length' x 128>
    get_array_of_notes(str, Mode.BOOLEANS, True)     -> <np.ndarray [bool],                size: 'grid length' x 128>
    
    get_array_of_notes(str, Mode.VELOCITIES, False)  -> <np.ndarray [float],               size: 'tracks' x 'grid length' x 128>
    get_array_of_notes(str, Mode.VELOCITIES, True)   -> <np.ndarray [float],               size: 'grid length' x 128>
    
    get_array_of_notes(str, Mode.NOTES, False)       -> <np.ndarray [None | SeparateNote], size: 'tracks' x 'grid length' x 128>
    get_array_of_notes(str, Mode.NOTES, True)        -> <np.ndarray [None | SeparateNote], size: 'grid length' x 128>
