'''Basic metrics calculating functions for CTG signals

TODO:
'''

import numpy as np

def calculate_SDNN(ctg_signal):
    '''Calculates standard deviation of bpm/sample intervals

    Args:
        ctg_signal (2darray): The (signal_length, 1) signal bpm/sample

    Returns:
        sdnn: The standard deviation of bpm for the signal

    TODO:

    '''

    return round(np.std(ctg_signal), 2)


def calculate_SDANN(ctg_signal, interval_length):
    '''Calculates standard deviation average for intervals with duration
    interval_length samples

    Args:
        ctg_signal (2darray): The (signal_length, 1) signal bpm/sample
        interval_length (int): The duration of intervals in seconds

    Returns:
        sdann_v: The standard deviation average of bpm for the signal

    TODO:

    '''

    # Split the signal in intervals of interval_length length
    parts = np.array_split(ctg_signal,
                           round(ctg_signal.shape[0]/interval_length))

    # Calculate sdnn for each part
    sdnn_lst = [calculate_SDNN(part) for part in parts]

    return sum(sdnn_lst)/len(sdnn_lst)