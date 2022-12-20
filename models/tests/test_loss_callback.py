from models.loss_callback import LossCallback


def test_calls_back_with_loss():
    called_loss = None

    def func(epoch, loss):
        nonlocal called_loss
        called_loss = loss
    callback = LossCallback(func)

    callback.on_epoch_end(1, {'loss': 12.0})

    assert called_loss == 12.0


def test_calls_back_with_epoch():
    called_epoch = None

    def func(epoch, loss):
        nonlocal called_epoch
        called_epoch = epoch
    callback = LossCallback(func)

    callback.on_epoch_end(1, {'loss': 12.0})

    assert called_epoch == 1
