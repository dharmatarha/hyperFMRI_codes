import numpy as np
#import matplotlib.pyplot as mplot
from numpy.random import default_rng
from math import pi


def polar2z(r,theta):
    """
    Polar coordinates to cartesian. Works on arrays as well (element-wise). Intended use is with double arrays.

    Inputs:
    r:          Magnitude
    theta:      Angle in radians

    Output:
    z:          Complex array.
    """
    return r * np.exp( 1j * theta )


def z2polar(z):
    """
    Cartesian coordinates to polar. Works on arrays as well (element-wise). Intended use is with double arrays.

    Input:
    z:          Complex array.

    Outputs:
    r:          Magnitude
    theta:      Angle in radians
    """
    return np.abs(z), np.angle(z)


def phase_scrambling(data_matrix, fft_axis=0):
    """
    FOR REAL DATA ONLY, NOT COMPLEX!

    Phase-scrambling function for matrices. Preserves the original covariance structure.

    After FFT, we add a random phase vector to the FFT components of all time series / vars and do inverse FFT,
    as described in Prichard and Theiler (1994, Generating surrogate data for time series with several
    simultaneously measured variables. Physical review letters, 73(7), 951).

    The returned phase-scrambled data has the same power spectrum as the original but is linearly independent
    (zero expected correlation). Covariance structure is preserved, meaning that linear dependencies
    across time series is the same in the phase-scrambled data as in the original.

    Inputs:
    data_matrix:        2D numpy array of reals. Time series (Vars) X samples by default,
                        set fft_axis if samples X time series.
    fft_axis:           Axis along which FFT / iFFT is calculated. Defaults to 0,
                        meaning that FFT is calculated across rows (= each column is a separate time series / var)

    Outputs:
    data_scrambled:     2D numpy array of reals, contains the phase-scrambled data.
                        Same size and dimensions as input "data_matrix".
                        Returns 0 if input checks failed.

    TODO:
    - missing tests: (1) compare original FFT amplitudes to scrambled data FFT amplitudes
                     (2) compare original covariance matrix to scrambled data covariance matrix
                     (3) check if correlations between original and corresponding scrambled time series are around 0
    - measure timing, sanity check against per var (per voxel) calculations
    - look into implementation with FFTW, which is supposedly faster with repetitive usage (our use case)
    """

    # input checks
    if not isinstance(data_matrix, np.ndarray) or len(data_matrix.shape) != 2 or np.iscomplex(data_matrix):
        print('Input arg "data_matrix" should be a 2D numpy array of reals!')
        return 0
    if fft_axis not in [0, 1]:
        print('Input arg "fft_axis" should be 0 or 1!')
        return 0

    # if fft_axis != 0, transpose the data
    transposeFlag = False
    if fft_axis == 1:
        data_matrix = np.transpose(data_matrix)
        transposeFlag = True

    # do forward FFT, use version for reals, treat data as if vars were in columns
    data_fft = np.fft.rfft(data_matrix, axis=0)
    fft_len = data_fft.shape[0]

    # convert to polar coordinates (amplitude/magnitude + phase)
    data_fft_amp = np.abs(data_fft)
    data_fft_angle = np.angle(data_fft)

    # get random phase vector  (values between 0 - 2pi) for all FFT components that are not real by definition
    rng = default_rng()  # new recommended method for random values
    if data_matrix.shape[0] % 2 == 0:  # if even, first and last components are real
        rand_phases = np.hstack(([0] ,((rng.random((data_fft.shape[0]-2)) * 2 * pi) * 1j), [0]))
    else:  # otherwise only the first component is real
        rand_phases = np.hstack(([0], ((rng.random((data_fft.shape[0] - 1)) * 2 * pi) * 1j)))

    # add random phases to the angles of FFT components of all time series / vars,
    # addition is with broadcasting (newaxis is needed for broadcasting)
    data_fft_angle_rand = data_fft_angle + rand_phases[:, np.newaxis]

    # transform back from polar to cartesian, using the randomized phases but the original magnitude / amplitude values
    data_scrambled_fft = data_fft_amp * np.exp(1j * data_fft_angle_rand)  # returns complex FFT coefficients

    # do inverse FFT
    data_scrambled = np.fft.irfft(data_scrambled_fft, axis=0)

    # transpose if necessary
    if transposeFlag:
        data_scrambled = np.transpose(data_scrambled)

    return data_scrambled





