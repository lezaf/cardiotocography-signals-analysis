'''Basic preprocessing functions for CTG signals for noise handling

TODO:
'''

import numpy as np


def remove_zero_parts_with_threshold(arr, threshold):
    '''Removes the intermediate zero parts from signal that have length
        equal or above a threshold

    Preconditions:
        - arr has no leading or trailing zeros

    Args:
        arr (2darray): The (signal_length, 1) signal to remove zero parts from

    Returns:
        res (2darray): The signal with intermediate zero parts removed with
                        same shape as input

    TODO:
        - fix double space complexity inefficiency, if possible
            (e.g. in-place calculation of new array instead of res)

    '''

    non_zero_indices = np.flatnonzero(arr)

    # get the distances between the non-zero values of arr
    non_zero_diffs = np.diff(non_zero_indices, prepend=0)

    # set the distances above threshold equal to 1, i.e. eliminate the
    # intermediate zero part
    non_zero_diffs[non_zero_diffs > threshold] = 1

    # calculate the new indices of non-zero values
    non_zero_diffs_cs = np.cumsum(non_zero_diffs)
    res = np.zeros((non_zero_diffs_cs[-1] + 1, 1))

    # construct array without the zero parts
    res[non_zero_diffs_cs] = arr[non_zero_indices]

    return res


def apply_linear_interpolation(arr):
    '''Interpolates arr on zero values

    Args:
        arr (2darray): The (signal_length, 1) signal

    Returns:
        arr (2darray): The signal with its zero values interpolated

    TODO:

    '''

    interpolated_values = np.interp(np.where(arr == 0)[0],
                                    np.flatnonzero(arr),
                                    arr[arr != 0].flatten())

    arr[arr == 0] = interpolated_values

    return arr


def apply_linear_interpolation_below_threshold(arr, threshold):
    '''Interpolates arr on values equal or below threshold

    Args:
    arr (2darray): The (signal_length, 1) signal

    Returns:
    arr (2darray): The interpolated signal

    TODO:

    '''

    interpolated_values = np.interp(np.where(arr <= threshold)[0],
    np.where(arr > threshold)[0],
    arr[arr > threshold].flatten())

    arr[arr <= threshold] = interpolated_values

    return arr


def apply_linear_interpolation_above_threshold(arr, threshold):
    '''Interpolates arr on values equal or above threshold

    Args:
        arr (2darray): The (signal_length, 1) signal

    Returns:
        arr (2darray): The interpolated signal

    TODO:

    '''

    interpolated_values = np.interp(np.where(arr >= threshold)[0],
                                    np.where(arr < threshold)[0],
                                    arr[arr < threshold].flatten())

    arr[arr >= threshold] = interpolated_values

    return arr