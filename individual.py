import numpy as np
import random
from scipy.io.wavfile import write
from fitness import *

class Individual:
    HIGHEST_PITCH = 27
    NUM_PITCHES = 32
    DURATION = 0.3
    SAMPLE_RATE = 44100
    PITCH_TO_FREQ = {
        0:  0,
        1:  174.61,  2: 185.00, 3:  196.00, 4:  207.65, 5:  220.00, 6:  233.08,
        7:  246.94,  8: 261.63, 9:  277.18, 10: 293.66, 11: 311.13, 12: 329.63,
        13: 349.23, 14: 369.99, 15: 392.00, 16: 415.30, 17: 440.00, 18: 466.16,
        19: 493.88, 20: 523.25, 21: 554.37, 22: 587.33, 23: 622.25, 24: 659.25,
        25: 698.46, 26: 739.99, 27: 783.99,
    }

    def __init__(self, pitches = None):
        if pitches is None:
            self.pitches = [
                random.randint(i % 4 == 0, Individual.HIGHEST_PITCH) 
                for i in range(Individual.NUM_PITCHES)
            ]
        else:
            self.pitches = pitches
        self.fitness = self.compute_fitness()

    def compute_fitness(self):
        return fitness(self)

    def generate_music(self):
        freqs = [Individual.PITCH_TO_FREQ[p] for p in self.pitches]
        waveform = np.array([], dtype=np.float32)
        i = 0
        while i < Individual.NUM_PITCHES:
            n_duration = 1
            freq = freqs[i]
            i += 1
            while i < Individual.NUM_PITCHES and self.pitches[i] == 0:
                n_duration += 1
                i += 1
            duration = n_duration * Individual.DURATION
            t = np.linspace(0, duration, int(Individual.SAMPLE_RATE * duration), endpoint=False)
            wave = 0.5 * np.sin(2 * np.pi * freq * t)
            waveform = np.concatenate((waveform, wave))
        waveform = (waveform * 32767).astype(np.int16)
        write("output.wav", Individual.SAMPLE_RATE, waveform)