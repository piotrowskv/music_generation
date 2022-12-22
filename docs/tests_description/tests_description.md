---
title: Music generation project
subtitle: Deliverable 4, tests description
author:
  - Weronika Piotrowska
  - Szymon Górski
  - Marcin Wojnarowski
published: true
date: December, 2022
urlcolor: cyan
geometry: margin=3.5cm
---

<!-- compile to pdf using `pandoc tests_description.md -o tests_description.pdf` -->

> Document describing what was tested with a non-exhaustive listing of example tests.

## Midi module

This module decodes and encodes midi files into structures digestible by our models. Here we tested individually the encoder, decoder, and dataset downloader.

### Bach dataset downloader

- Test verifying that the dataset is correctly downloaded to some specified path

```python
def test_downloads_dataset(tmpdir):
    path = Path(tmpdir)

    download_bach_dataset(path)

    assert path.joinpath('bach.zip').exists()
    assert path.joinpath('bach').is_dir()
```

- Test verifying that the provided path cannot be a file

```python
def test_fails_if_path_is_file(tmpdir):
    path = Path(tmpdir).joinpath('file.txt')
    path.touch()

    with pytest.raises(AssertionError):
        download_bach_dataset(path)
```

### Decoder

- Test verifying the correctness of the midi tracks combiner

```python
def test_combine_and_clean_tracks():  # test_tempos_velocities_and_polyphony.mid used
    file = MidiFile(filepath)
    tracks = file.tracks[1:]
    out_track = combine_and_clean_tracks(tracks)

    assert isinstance(out_track, MidiTrack)
    assert out_track == expected_midi_track
```

- Test verifying the tempo extractor

```python
def test_export_tempo_array():  # test_tempos_velocities_and_polyphony.mid used
		expected_tempos = [500000] * 80

    tempos = export_tempo_array(filepath)

    assert isinstance(tempos, list)
    assert tempos == expected_tempos
```

- Test verifying tonal features extraction

```python
def test_get_list_of_tonal_features():
    tonal_features = get_list_of_tonal_features(
			copy.deepcopy(expected_events),
			copy.deepcopy(expected_tempos)
		)

    assert isinstance(tonal_features, list)
    assert tonal_features == expected_tonal
```

### Encoder

- Test verifying the correct encoding of metadata information

```python
def test_get_tempo_meta_messages():
    meta_track = get_tempo_meta_messages(input_tempos, float(15))

    assert isinstance(meta_track, MidiTrack)
    assert meta_track == expected_meta
```

- Test verifying the correct encoding of a midi track

```python
def test_get_note_messages_from_2d_array():
    input_array = np.load(input_array_path, allow_pickle=True)
    track = get_note_messages_from_2d_array(input_array, 0, float(15))

    assert isinstance(track, MidiTrack)
    assert track == expected_track
```

## Models module

This module defines and trains models for music generation. It utilizes the midi module and trains on arbitrary datasets. To test models we track their performance using various metrics:

1. Loss function
2. Accuracy
3. Music quality

Testing those fully requires completed models, so for now we present tests of some side functionality.

- Test verifying the loss function tensorflow callback tracker

```python
def test_calls_back_with_loss():
    called_loss = None

    def func(epoch, loss):
        nonlocal called_loss
        called_loss = loss
    callback = LossCallback(func)

    callback.on_epoch_end(1, {'loss': 12.0})

    assert called_loss == 12.0
```

- Test verifying the LSTM model dataset creation

```python
def test_lstm_creates_dataset():
    lstm = MusicLstm(5)

    xtrain, ytrain = lstm.create_dataset([
        (
            [[[1, 2, 3], [4, 5, 6]], [[10, 11, 12], [13, 14, 15]]],
            [[8, 8, 8], [9, 9, 9]],
        ),
        (
            [[[-1, -2, -3], [-4, -5, -6]], [[-10, -11, -12], [-13, -14, -15]]],
            [[-8, -8, -8], [-9, -9, -9]],
        ),
    ])

    assert (xtrain == np.array([[[1, 2, 3], [4, 5, 6]], [[10, 11, 12], [13, 14, 15]], [
        [-1, -2, -3], [-4, -5, -6]], [[-10, -11, -12], [-13, -14, -15]]])).any()
    assert (ytrain == np.array(
        [[8, 8, 8], [9, 9, 9], [-8, -8, -8], [-9, -9, -9]])).any()
```

- Test verifying the generation of ngrams for the markov chain

```python
def test_generate_n_grams():
    model = MarkovChain()

    model.data = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 0]]
    model.generate_n_grams(3)

    assert model.n_grams_list == list(set([
        (1, 2, 3), (2, 3, 4), (3, 4, 5), (6, 7, 8), (7, 8, 9), (8, 9, 0)]))
```

## Backend module

This module is for a backend server which bridges the frontend interface with the models. Here testing mostly revolves around checking the correctness of endpoints.

- Test verifying the `/models` endpoint

```python
def test_get_models():
    response = client.get("/models")
    assert response.status_code == 200

    data = response.json()['variants']
    assert len(data) == len(
        SupportedModels), 'Returned less models than supported'

    ids = [d['id'] for d in data]
    assert len(set(ids)) == len(ids), 'IDs are not unique'
```

- Test verifying the start session endpoint

```python
def test_train_session():
    response = client.post("/training/session")
    assert response.status_code == 200
```

## Frontend module

This module is the user interface for training models and generating new music. Testing involves UI, business logic, and integration tests.

- Test verifying the theme configuration

```ts
function renderTest() {
  function TestComponent() {
    const theme = useThemeContext();

    return (
      <>
        {(Object.keys(theme) as (keyof typeof theme)[]).map((e) => (
          <div key={e} data-testid={e}>
            {theme[e].toString()}
          </div>
        ))}
      </>
    );
  }

  render(<TestComponent />);
}

test("has correct default values", () => {
  renderTest();

  expect(screen.getByTestId("mode")).toHaveTextContent(
    ThemeMode.system.toString()
  );
});
```

- Test verifying real connection with a running server

```ts
test("happy path", async () => {
  const models = await apiClient.getModelVariants();

  // we got any response
  expect(models).toBeTruthy();

  // we got all models
  expect(models.variants.length).toBe(3);

  // all fields are present
  for (const v of models.variants) {
    expect(v.description).toBeTruthy();
    expect(v.id).toBeTruthy();
    expect(v.name).toBeTruthy();
  }
});
```

- Test verifying UI behavior of a component

```ts
test("renders message", async () => {
  const f = vi.fn();
  render(<ErrorMessage onRetry={f}>Failed to load models</ErrorMessage>);

  expect(screen.findByText("Failed to load models")).toBeTruthy();
});

test("calls callback on refresh", async () => {
  const f = vi.fn();
  render(<ErrorMessage onRetry={f}>Failed to load models</ErrorMessage>);
  (await screen.findByRole("button")).click();

  expect(f).toHaveBeenCalledOnce();
});
```
