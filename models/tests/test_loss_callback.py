from models.loss_callback import LossCallback


def test_calls_back_with_loss():
    called_loss = None

    def func(args):
        nonlocal called_loss
        (epoch, loss) = args[0]
        called_loss = loss
    callback = LossCallback(func)

    callback.on_epoch_end(1, {'loss': 12.0})

    assert called_loss == 12.0


def test_calls_back_with_epoch():
    called_epoch = None

    def func(args):
        nonlocal called_epoch
        (epoch, loss) = args[0]
        called_epoch = epoch
    callback = LossCallback(func)

    callback.on_epoch_end(1, {'loss': 12.0})

    assert called_epoch == 2
