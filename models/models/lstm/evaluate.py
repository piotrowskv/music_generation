from pathlib import Path

from matplotlib import pyplot as plt
from midi.bach import download_clean_dataset
from sklearn.model_selection import train_test_split

from .model import MusicLstm


def plot_metrics(metrics: set[str], history: dict[str, list[float]]):
    save_dir = Path('evaluation/lstm')
    save_dir.mkdir(exist_ok=True, parents=True)

    for metric in metrics:
        plt.clf()

        plt.plot(history[metric])
        plt.plot(history[f'val_{metric}'])

        plt.title(f'LSTM {metric}')
        plt.ylabel(metric)
        plt.xlabel('epoch')
        plt.legend(['train', 'validation'], loc='upper left')

        plt.savefig(save_dir.joinpath(f'{metric}.png'))


if __name__ == '__main__':
    # get dataset
    dataset_path = Path('data')
    download_clean_dataset(dataset_path)
    files = list(dataset_path.joinpath('midi_dataset/3_tracks').glob("*.mid"))

    # create model and prepare data
    metrics = ['accuracy']
    model = MusicLstm(metrics=metrics)

    dataset = [model.prepare_data(f) for f in files]
    X, Y = model.create_dataset(dataset)
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

    # fit and plot intermediate metrics
    history = model.model.fit(
        x_train,
        y_train,
        epochs=20,
        batch_size=64,
        validation_split=0.1
    )
    plot_metrics({'loss', *metrics}, history.history)

    # print test metrics
    eval_results = model.model.evaluate(x_test, y_test, batch_size=64, return_dict=True)
    print(eval_results)
