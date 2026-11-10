import numpy as np
import pandas as pd

from technical.qtpylib import awesome_oscillator, numpy_rolling_mean, numpy_rolling_window


def test_rolling_window_shorter_than_period_is_empty():
    data = np.array([1.0, 2.0, 3.0])

    windows = numpy_rolling_window(data, 5)

    assert windows.shape == (0, 5)
    mean = numpy_rolling_mean(data, 5)
    assert mean.shape == (3,)
    assert np.isnan(mean).all()


def test_rolling_mean_keeps_warmup_nan():
    data = np.array([1.0, 2.0, 3.0, 4.0])

    mean = numpy_rolling_mean(data, 3)

    assert np.isnan(mean[:2]).all()
    np.testing.assert_allclose(mean[2:], [2.0, 3.0])


def test_rolling_window_length_equal_to_window_has_one_row():
    data = np.array([1.0, 2.0, 3.0, 4.0])

    windows = numpy_rolling_window(data, len(data))

    assert windows.shape == (1, 4)
    np.testing.assert_array_equal(windows[0], data)
    mean = numpy_rolling_mean(data, len(data))
    assert mean.shape == (4,)
    assert np.isnan(mean[:-1]).all()
    np.testing.assert_allclose(mean[-1], 2.5)


def test_rolling_window_full_period_is_unchanged():
    data = np.array([1.0, 2.0, 3.0, 4.0])

    windows = numpy_rolling_window(data, 3)

    assert windows.shape == (2, 3)
    np.testing.assert_array_equal(windows[0], [1.0, 2.0, 3.0])
    np.testing.assert_array_equal(windows[1], [2.0, 3.0, 4.0])


def test_awesome_oscillator_short_frame_is_nan():
    frame = pd.DataFrame(
        {"high": [1.0, 2.0, 3.0], "low": [0.5, 1.5, 2.5]},
    )

    result = awesome_oscillator(frame)

    assert len(result) == 3
    assert result.isna().all()
