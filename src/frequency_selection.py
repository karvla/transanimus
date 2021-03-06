from time import sleep, time
import numpy as np
from reader import Reader
from plotter import Plotter
from scipy import signal
from scipy.integrate import simps


from time import time
def map_peaks(peaks):
    """ Maps peaks to be in an audible range """

    pentagon = [1/1, 32/27, 4/3, 3/2, 16/9]
    scale = []
    for n in range(1, 50):
        scale += [i*n for i in pentagon]

    peaks = np.array(scale)[np.int16(peaks)]*50 + 440
    peaks += np.random.random(peaks.shape)
    return peaks
    
def periodogram(u, t, n_win=4):
    """ Returns the power spectral density for different
        frequencies using welch method. """
    sf = 200
    win = int(len(t) / n_win)
    freqs, power = signal.welch(u, sf, nperseg=win)
    return freqs, power


def pad(u, n=256):
    zeros = np.zeros(256)
    return np.concatenate((zeros, u, zeros), axis=0)


def relative_power(a, b, freqs, psd):
    """
    Computes the relative power of the signal between a hz and b hz.
    """
    dx = freqs[1] - freqs[0]

    index = np.logical_and(freqs >= a, freqs <= b)
    index_50_hz = np.logical_and(freqs >= 40, freqs <= 60)

    ab_power = simps(psd[index], dx=dx)
    total_power = simps(psd, dx=dx) - simps(psd[index_50_hz], dx=dx)
    return round(ab_power / total_power, 3)


def band_power(freqs, psd):
    delta = relative_power(0.5, 3, freqs, psd)
    theta = relative_power(3, 8, freqs, psd)
    alpha = relative_power(8, 12, freqs, psd)
    beta = relative_power(12, 38, freqs, psd)
    gamma = relative_power(38, 42, freqs, psd)
    return delta, theta, alpha, beta, gamma


def heartrate(u, t):
    freqs, psd = periodogram(u, t, 2)
    index_max = np.argmax(psd)
    return freqs[index_max]


def freq_peaks(freqs, power, n=1):
    """ Return the top n peaks from the freqs and power. """
    power_dt = np.gradient(power, freqs)
    peaks = list(filter(lambda x: abs(x[2]) < 0.05, zip(freqs, power, power_dt)))
    peaks_by_power = sorted(peaks, key=lambda x: abs(x[1]), reverse=True)

    peaks = [(f, p) for f, p, _ in peaks_by_power[:n]]
    return peaks


if __name__ == "__main__":
    freq = np.arange(0, 10, 0.1)
    power = np.sin(freq)
    max_pair = freq_peaks(freq, power, 3)
    print(max_pair)
