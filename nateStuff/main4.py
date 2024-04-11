import tkinter as tk
from tkinter import filedialog
import wave
import numpy as np
import pygame
from io import BytesIO
import threading

import pyaudio
import struct

from scipy.signal import resample

class AudioTrimmer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Audio Trimmer")
        self.geometry("800x400")

        self.audio_data = None
        self.audio_rate = None
        self.waveform_data = None
        self.start_marker = 0
        self.end_marker = 0
        self.loading_thread = None

        self.canvas = tk.Canvas(self, width=800, height=200, bg="white")
        self.canvas.pack()

        self.bar1_marker = None
        self.bar2_marker = None

        self.canvas.bind("<Button-1>", self.place_marker)

        self.start_marker_line = self.canvas.create_line(0, 0, 0, 200, fill="green", width=2)
        self.end_marker_line = self.canvas.create_line(800, 0, 800, 200, fill="red", width=2)

        self.load_button = tk.Button(self, text="Load Audio", command=self.load_audio)
        self.load_button.pack(pady=10)

        self.preview_button = tk.Button(self, text="Preview", command=self.preview_audio)
        self.preview_button.pack(pady=10)

        self.save_button = tk.Button(self, text="Save Trimmed Audio", command=self.save_audio)
        self.save_button.pack(pady=10)

        self.canvas.bind("<B1-Motion>", self.update_markers)

    def load_audio(self):
        if self.loading_thread and self.loading_thread.is_alive():
            return

        file_path = filedialog.askopenfilename(defaultextension=".wav", filetypes=[("WAV Files", "*.wav")])
        if file_path:
            self.loading_thread = threading.Thread(target=self.load_audio_thread, args=(file_path,))
            self.loading_thread.start()

    def load_audio_thread(self, file_path):
        with wave.open(file_path, "r") as audio_file:
            num_channels = audio_file.getnchannels()
            sample_width = audio_file.getsampwidth()
            self.audio_rate = audio_file.getframerate()
            num_frames = audio_file.getnframes()

            # Read audio data from the file
            raw_data = audio_file.readframes(num_frames)

            # Convert raw data to a numpy array based on the sample width
            if sample_width == 1:
                dtype = np.uint8
            elif sample_width == 2:
                dtype = np.int16
            else:
                raise ValueError("Unsupported sample width")

            # Reshape the audio data based on the number of channels
            if num_channels == 1:
                self.audio_data = np.frombuffer(raw_data, dtype=dtype)
            else:
                self.audio_data = np.frombuffer(raw_data, dtype=dtype).reshape(-1, num_channels)

            self.compute_waveform_data()
        self.draw_waveform()

    def compute_waveform_data(self):
        audio_length = len(self.audio_data)
        step_size = audio_length // 800  # Choose a step size to downsample
        self.waveform_data = []
        if self.audio_data.ndim == 1:  # Single channel
            for i in range(0, audio_length, step_size):
                chunk = self.audio_data[i:i+step_size]
                if chunk.any():
                    max_value = np.max(np.abs(chunk))
                    normalized_max = max_value / 32767  # Assuming 16-bit audio
                    self.waveform_data.append((i * 800 / audio_length, 100 - (normalized_max * 80)))
        else:  # Multiple channels
            for i in range(0, audio_length, step_size):
                chunk = self.audio_data[i:i+step_size]
                if chunk.any():
                    max_values = np.max(np.abs(chunk), axis=1)
                    normalized_max = np.max(max_values) / 32767  # Assuming 16-bit audio
                    self.waveform_data.append((i * 800 / audio_length, 100 - (normalized_max * 80)))



    def draw_waveform(self):
        self.canvas.delete("waveform")
        if self.waveform_data is not None:
            for x, y in self.waveform_data:
                self.canvas.create_line(x, y, x, y + 1, tags="waveform", fill="blue")

    def place_marker(self, event):
        x = event.x
        if x < 0:
            x = 0
        elif x > 800:
            x = 800

        if self.bar1_marker is None:
            self.bar1_marker = x
            self.canvas.create_line(x, 0, x, 200, fill="green", width=2, tags="marker")
        elif self.bar2_marker is None:
            self.bar2_marker = x
            self.canvas.create_line(x, 0, x, 200, fill="red", width=2, tags="marker")
            # Preview or save the trimmed audio between bar1_marker and bar2_marker here
            self.preview_save_audio()

    def update_markers(self, event):
        x = event.x
        if x < 0:
            x = 0
        elif x > 800:
            x = 800

        # Check if the distance between start and end markers is small enough for a valid selection
        if abs(x - self.start_marker) < 10:
            return

        if x < self.start_marker:
            self.canvas.coords(self.start_marker_line, x, 0, x, 200)
            self.start_marker = int(x * len(self.audio_data) / 800)
        else:
            self.canvas.coords(self.end_marker_line, x, 0, x, 200)
            self.end_marker = int(x * len(self.audio_data) / 800)


    def preview_audio(self):
        if self.audio_data is not None and self.bar1_marker is not None and self.bar2_marker is not None:
            start_index = int(min(self.bar1_marker, self.bar2_marker) * len(self.audio_data) / 800)
            end_index = int(max(self.bar1_marker, self.bar2_marker) * len(self.audio_data) / 800)

            trimmed_data = self.audio_data[start_index:end_index]
            original_duration = (end_index - start_index) / self.audio_rate

            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(2),
                            channels=1,
                            rate=self.audio_rate,
                            output=True)

            trimmed_data_int = trimmed_data.tolist()

            data = struct.pack('h' * len(trimmed_data_int), *trimmed_data_int)
            stream.write(data)
            stream.stop_stream()
            stream.close()
            p.terminate()


    def save_audio(self):
        if self.audio_data is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV Files", "*.wav")])
            if file_path:
                start_index = int(min(self.bar1_marker, self.bar2_marker) * len(self.audio_data) / 800)
                end_index = int(max(self.bar1_marker, self.bar2_marker) * len(self.audio_data) / 800)
                trimmed_data = self.audio_data[start_index:end_index]
                resampled_data = resample(trimmed_data, len(trimmed_data))

                with wave.open(file_path, "w") as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(self.audio_rate)
                    wav_file.writeframes(resampled_data.tobytes())



if __name__ == "__main__":
    app = AudioTrimmer()
    app.mainloop()