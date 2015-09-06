# coding:utf-8

"""
functions to extract features from file
and make fingerprints hashes

"""

#######################################################
from scipy.io.wavfile import read
from pylab import plot, show, subplot, specgram
import numpy as np

import matplotlib.pyplot as plt

from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (generate_binary_structure,
                                      iterate_structure, binary_erosion)
import hashlib

from operator import itemgetter



# CONSTANTS #


IDX_FREQ_I = 0
IDX_TIME_J = 1

# Size of the FFT window, affects frequency granularity
DEFAULT_WINDOW_SIZE = 4096

# Ratio by which each sequential window overlaps the last and the
# next window. Higher overlap will allow a higher granularity of offset
# matching, but potentially more fingerprints.
DEFAULT_OVERLAP_RATIO = 0.5

# Degree to which a fingerprint can be paired with its neighbors --
# higher will cause more fingerprints, but potentially better accuracy.
DEFAULT_FAN_VALUE = 20

# Minimum amplitude in spectrogram in order to be considered a peak.
# This can be raised to reduce number of fingerprints, but can negatively
# affect accuracy.
DEFAULT_AMP_MIN = 10

# Number of cells around an amplitude peak in the spectrogram in order
# for Dejavu to consider it a spectral peak. Higher values mean less
# fingerprints and faster matching, but can potentially affect accuracy.
PEAK_NEIGHBORHOOD_SIZE = 15

# Thresholds on how close or far fingerprints can be in time in order
# to be paired as a fingerprint. If your max is too low, higher values of
# DEFAULT_FAN_VALUE may not perform as expected.
MIN_HASH_TIME_DELTA = 0
MAX_HASH_TIME_DELTA = 200

# If True, will sort peaks temporally for fingerprinting;
# not sorting will cut down number of fingerprints, but potentially
# affect performance.
PEAK_SORT = True







def read_wav_file(filepath):
    """
    emulate mp3_handler so example at the end could work
    """
    rate, data = read(filepath)
    return rate, data



def process_file(rate, data, original=None, vizualize=False):
    """
    prepare fingerprints
    """

    print len(data)
    print rate

    if vizualize:
        subplot(211)
        plot(range(len(data)), data)
        subplot(212)


    arr2D = specgram(
        data,
        NFFT=DEFAULT_WINDOW_SIZE,
        Fs=rate,
        window=None,
        noverlap=int(DEFAULT_WINDOW_SIZE * DEFAULT_OVERLAP_RATIO))[0]


    # apply log transform since specgram() returns linear array
    arr2D = 10 * np.log10(arr2D)
    arr2D[arr2D == -np.inf] = 0  # replace infs with zeros

    # find local maxima
    local_maxima = get_2D_peaks(arr2D, visualize=vizualize, amp_min=DEFAULT_AMP_MIN)
    result = set()

    # get hashes from peaks
    hashes = generate_hashes(local_maxima, fan_value=DEFAULT_FAN_VALUE)
    result |= set(hashes)

    if vizualize:
        show()



    #### STORE TO FILE
    #if original:
        #original = original.split('.')[0]

        #import pickle
        #print original
        #file_res = open(original+'_hashes','w')
        #pickle.dump(result, file_res)
        #file_res.close()

    return result



def get_2D_peaks(arr2D, visualize=False, amp_min=DEFAULT_AMP_MIN):
    """
    extract peaks from spectrogram
    ###########################################################################
    #http://stackoverflow.com/questions/3684484/peak-detection-in-a-2d-array
    ###########################################################################
    # http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.morphology.iterate_structure.html#scipy.ndimage.morphology.iterate_structure
    """

    # define an 4-connected neighborhood
    #   #1#
    #   111
    #   #1#
    struct = generate_binary_structure(2, 1)

    # define an 8-connected neighborhood
    #struct = generate_binary_structure(2, 2)

    # iterate this structure to get larger mask with param
    neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD_SIZE)

    # find local maximum using our filter shape
    #apply the local maximum filter; all pixel of maximal value
    #in their neighborhood are set to 1
    local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D

    #local_max is a mask that contains the peaks we are
    #looking for, but also the background.
    #In order to isolate the peaks we must remove the background from the mask.
    background = (arr2D == 0)

    #a little technicality: we must erode the background in order to
    #successfully subtract it form local_max, otherwise a line will
    #appear along the background border (artifact of the local maximum filter)
    eroded_background = binary_erosion(background, structure=neighborhood,
                                       border_value=1)

    # Boolean mask of arr2D with True at peaks
    #we obtain the final mask, containing only peaks,
    #by removing the background from the local_max mask
    detected_peaks = local_max - eroded_background

    # extract peaks
    amps = arr2D[detected_peaks]
    print 'arr2D', len(arr2D)
    print 'amps', len(amps)

    j, i = np.where(detected_peaks)

    # filter peaks
    amps = amps.flatten()
    peaks = zip(i, j, amps)
    peaks_filtered = [x for x in peaks if x[2] > amp_min]  # freq, time, amp

    # get indices for frequency and time
    frequency_idx = [x[1] for x in peaks_filtered]
    time_idx = [x[0] for x in peaks_filtered]

    if visualize:
        # scatter of the peaks
        fig, ax = plt.subplots()
        ax.imshow(arr2D)
        ax.scatter(time_idx, frequency_idx)
        ax.set_xlabel('Time')
        ax.set_ylabel('Frequency')
        ax.set_title("Spectrogram")
        plt.gca().invert_yaxis()

        # save or show
        plt.show()
        #plt.savefig('fingerprints.png')

    return zip(frequency_idx, time_idx)




def generate_hashes(peaks, fan_value=DEFAULT_FAN_VALUE):
    """
    Hash list structure:
       sha1_hash    time_offset
    [(e05b341a9b77a51fd26, 32), ... ]
    """
    if PEAK_SORT:
        peaks.sort(key=itemgetter(1))

    for i in range(len(peaks)):
        for j in range(1, fan_value):
            if (i + j) < len(peaks):

                freq1 = peaks[i][IDX_FREQ_I]
                freq2 = peaks[i + j][IDX_FREQ_I]
                t1 = peaks[i][IDX_TIME_J]
                t2 = peaks[i + j][IDX_TIME_J]
                t_delta = t2 - t1

                if t_delta >= MIN_HASH_TIME_DELTA and t_delta <= MAX_HASH_TIME_DELTA:
                    h = hashlib.sha1(
                        "%s|%s|%s" % (str(freq1), str(freq2), str(t_delta)))
                    #yield (h.hexdigest(), t1)
                    yield h.hexdigest()




def zcr(rate, data, original_filename, visualize=False):
    """Computes zero crossing rate of frame"""

    zero_crossings = 0
    zero_cross = []

    for i in range(1, len(data)):
        if (data[i - 1] < 0 and data[i] > 0) or \
           (data[i - 1] > 0 and data[i] < 0) or \
           (data[i - 1] != 0 and data[i] == 0):

            zero_crossings += 1
            zero_cross.append(1)
        else:
            zero_cross.append(0)

    zero_crossing_rate = zero_crossings / float(len(data) - 1)
    print 'zero_crossing_rate', zero_crossing_rate


    if visualize:
        #plt.clf()
        plt.subplot(211)
        plt.plot(range(len(data)), data)

        subplot(212)
        plt.plot(range(len(zero_cross)), zero_cross)

        # save or show
        #plt.savefig(original_filename + 'zcr.png')
        show()

        #### save to pickle
        #import pickle
        #file_res = open(original_filename + '_zc', 'w')
        #pickle.dump(zero_cross, file_res)
        #file_res.close()

    return zero_crossing_rate







if __name__ == '__main__':

    """
    result .png files save to the same with file dir
    calculating zcr takes some time ~10sec afte closing visualized graphs

    """
    #TODO
    # retrieve file from data storage (via api?)

    import tempfile
    import commands
    import os

    def example(filename_mp3):

        temp = tempfile.NamedTemporaryFile()
        try:
            print 'temp:', temp
            print 'temp.name:', temp.name
            os.system("mpg123 --wav " + temp.name + " --8bit --rate 8000 --mono " + filename_mp3)

            #emulate mp3_handler read
            rate, data = read_wav_file(temp.name)

            #get fingerprints
            process_file(rate, data, filename_mp3, vizualize=True)

            #get zero crossing rate
            zcr(rate, data, filename_mp3, visualize=True)


        finally:
            # Automatically cleans up the file
            temp.close()

    filename_mp3 = '../../fixtures/white_america_526.mp3'
    example(filename_mp3)

















