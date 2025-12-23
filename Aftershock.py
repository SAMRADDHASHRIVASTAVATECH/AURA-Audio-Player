import sys

import math

import numpy as np

import time

import ctypes

import os



from PyQt6.QtWidgets import (

    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,

    QGridLayout, QLabel, QPushButton, QScrollArea, QFrame, QGroupBox,

    QComboBox, QMessageBox, QRadioButton, QButtonGroup, QSlider,

    QSizePolicy

)

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize, QPointF, QRectF

from PyQt6.QtGui import (

    QFont, QColor, QPainter, QLinearGradient, QPainterPath,

    QRadialGradient, QConicalGradient, QPen, QBrush, QPolygonF

)



try:

    import sounddevice as sd

    AUDIO_AVAILABLE = True

except ImportError:

    AUDIO_AVAILABLE = False

    print("CRITICAL: Install sounddevice -> pip install sounddevice numpy")



# ========================= SYSTEM OPTIMIZATIONS =========================



def set_high_priority():

    """ Force Windows to prioritize this audio process """

    try:

        if sys.platform == 'win32':

            import ctypes

            # HIGH_PRIORITY_CLASS = 0x00000080

            ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000080)

    except Exception:

        pass



set_high_priority()



# ========================= PRESETS LIBRARY =========================

PRESETS = {

    "🚀 EXTREME BOOSTERS": {

        "💣 BASS GOD":       {"bass": 3.0, "treble": 1.0, "loudness": 1.5, "spatial": 0.5, "color": "#FF0040"},

        "☢️ NUKE BASS":      {"bass": 5.0, "treble": 0.8, "loudness": 1.6, "spatial": 0.3, "color": "#D70000"},

        "💥 MEGA BOOM":      {"bass": 2.5, "treble": 1.2, "loudness": 1.8, "spatial": 0.6, "color": "#FF4500"},

        "👂 EAR RAPE":       {"bass": 4.0, "treble": 4.0, "loudness": 3.0, "spatial": 0.1, "color": "#000000"},

        "🔊 LOUDNESS MAX":   {"bass": 1.5, "treble": 1.5, "loudness": 2.5, "spatial": 0.2, "color": "#FFD700"},

        "💎 CRYSTAL CLEAR":  {"bass": 0.8, "treble": 3.5, "loudness": 1.4, "spatial": 0.6, "color": "#00CED1"},

        "⛰️ HIGH PEAKS":     {"bass": 1.0, "treble": 4.0, "loudness": 1.2, "spatial": 0.4, "color": "#E0FFFF"},

        "🔨 HARD HITTING":   {"bass": 3.5, "treble": 1.5, "loudness": 1.9, "spatial": 0.4, "color": "#8B0000"},

        "🌪️ TURBO":          {"bass": 2.5, "treble": 2.5, "loudness": 2.0, "spatial": 0.7, "color": "#FF8C00"},

        "📏 FLATTENED":      {"bass": 1.0, "treble": 1.0, "loudness": 1.0, "spatial": 0.0, "color": "#808080"},

    },

    "🌀 8D & SPATIAL FX": {

        "🌀 8D Motion":      {"bass": 1.0, "treble": 1.0, "loudness": 1.0, "spatial": 0.5, "pan_depth": 0.7, "pan_speed": 0.12, "phase_offset": 0.3, "delay_ms": 5, "head_shadow": 0.4, "distance": 0.3, "color": "#00FFFF"},

        "🌌 Galaxy Surround": {"bass": 1.5, "treble": 1.2, "loudness": 1.0, "spatial": 2.5, "pan_depth": 0.5, "pan_speed": 0.08, "phase_offset": 0.2, "delay_ms": 10, "head_shadow": 0.3, "distance": 0.5, "color": "#9400D3"},

        "😵 Dizzy Spin":      {"bass": 1.2, "treble": 1.2, "loudness": 1.0, "spatial": 1.8, "pan_depth": 1.0, "pan_speed": 0.8, "phase_offset": 0.5, "delay_ms": 2, "head_shadow": 0.6, "distance": 0.1, "color": "#FF00FF"},

        "🏟️ Wide Arena":      {"bass": 1.8, "treble": 1.0, "loudness": 1.2, "spatial": 1.5, "pan_depth": 0.2, "pan_speed": 0.05, "phase_offset": 0.1, "delay_ms": 15, "head_shadow": 0.2, "distance": 0.7, "color": "#4169E1"},

        "🧠 Brain Massage":   {"bass": 1.1, "treble": 0.8, "loudness": 0.9, "spatial": 2.0, "pan_depth": 0.8, "pan_speed": 0.2, "phase_offset": 0.6, "delay_ms": 5, "head_shadow": 0.5, "distance": 0.2, "color": "#FF69B4"},

        "🌑 Void":            {"bass": 2.0, "treble": 0.5, "loudness": 1.0, "spatial": 1.2, "pan_depth": 0.4, "pan_speed": 0.1, "phase_offset": 0.4, "delay_ms": 12, "head_shadow": 0.8, "distance": 0.8, "color": "#000000"},

    },

    "🕰️ DECADES": {

        "📼 80s Synth":      {"bass": 1.8, "treble": 1.8, "loudness": 1.2, "spatial": 0.8, "color": "#FF00FF"},

        "💿 90s Grunge":     {"bass": 1.6, "treble": 1.2, "loudness": 1.4, "spatial": 0.3, "color": "#556B2F"},

        "📀 2000s Pop":      {"bass": 1.4, "treble": 2.0, "loudness": 1.5, "spatial": 0.5, "color": "#00BFFF"},

        "🎷 50s Vinyl":      {"bass": 1.2, "treble": 0.6, "loudness": 1.0, "spatial": 0.1, "color": "#D2691E"},

        "🎸 70s Rock":       {"bass": 1.5, "treble": 1.5, "loudness": 1.2, "spatial": 0.4, "color": "#A52A2A"},

    },

    "🎵 GENRES: MODERN": {

        "🔥 Club":           {"bass": 2.5, "treble": 1.5, "loudness": 1.6, "spatial": 0.6, "color": "#FF1493"},

        "🎹 EDM":            {"bass": 2.2, "treble": 1.7, "loudness": 1.7, "spatial": 0.6, "color": "#00FF7F"},

        "🎤 Hip Hop":        {"bass": 2.8, "treble": 1.2, "loudness": 1.5, "spatial": 0.5, "color": "#9932CC"},

        "💊 Trap":           {"bass": 3.0, "treble": 1.8, "loudness": 1.6, "spatial": 0.4, "color": "#4B0082"},

        "🎸 Rock":           {"bass": 1.8, "treble": 1.8, "loudness": 1.4, "spatial": 0.4, "color": "#B22222"},

        "🤘 Metal":          {"bass": 2.0, "treble": 2.2, "loudness": 1.8, "spatial": 0.3, "color": "#2F4F4F"},

        "🥞 Pop":            {"bass": 1.4, "treble": 1.4, "loudness": 1.3, "spatial": 0.5, "color": "#FF69B4"},

        "🇰🇷 K-Pop":         {"bass": 1.6, "treble": 1.8, "loudness": 1.4, "spatial": 0.5, "color": "#FFB6C1"},

        "🕺 Disco":          {"bass": 2.0, "treble": 1.6, "loudness": 1.3, "spatial": 0.6, "color": "#DA70D6"},

        "🤖 Dubstep":        {"bass": 3.5, "treble": 2.0, "loudness": 1.6, "spatial": 0.7, "color": "#8A2BE2"},

        "🇯🇲 Reggae":        {"bass": 2.5, "treble": 1.2, "loudness": 1.3, "spatial": 0.6, "color": "#006400"},

        "🏠 House":          {"bass": 2.4, "treble": 1.4, "loudness": 1.5, "spatial": 0.6, "color": "#00FA9A"},

        "👽 Techno":         {"bass": 2.2, "treble": 1.3, "loudness": 1.5, "spatial": 0.4, "color": "#708090"},

        "🥁 Drum & Bass":    {"bass": 2.8, "treble": 1.8, "loudness": 1.7, "spatial": 0.5, "color": "#FF4500"},

        "🛋️ Lo-Fi":          {"bass": 1.8, "treble": 0.8, "loudness": 1.1, "spatial": 0.4, "color": "#D8BFD8"},

    },

    "🎻 GENRES: CLASSIC": {

        "🎻 Classical":      {"bass": 1.2, "treble": 1.4, "loudness": 1.1, "spatial": 0.8, "color": "#DAA520"},

        "🎷 Jazz":           {"bass": 1.5, "treble": 1.3, "loudness": 1.2, "spatial": 0.6, "color": "#D2691E"},

        "🎺 Blues":          {"bass": 1.4, "treble": 1.2, "loudness": 1.3, "spatial": 0.5, "color": "#4682B4"},

        "🤠 Country":        {"bass": 1.3, "treble": 1.5, "loudness": 1.3, "spatial": 0.4, "color": "#8B4513"},

        "🚜 Folk":           {"bass": 1.2, "treble": 1.4, "loudness": 1.1, "spatial": 0.3, "color": "#556B2F"},

        "🎩 Opera":          {"bass": 1.1, "treble": 1.6, "loudness": 1.4, "spatial": 0.9, "color": "#800000"},

        "☮️ Soul":           {"bass": 1.6, "treble": 1.1, "loudness": 1.2, "spatial": 0.5, "color": "#C71585"},

        "🕺 Funk":           {"bass": 2.0, "treble": 1.5, "loudness": 1.3, "spatial": 0.5, "color": "#FF8C00"},

        "🎹 Piano Solo":     {"bass": 1.1, "treble": 1.3, "loudness": 1.1, "spatial": 0.7, "color": "#F0E68C"},

        "🎻 Acoustic":       {"bass": 1.1, "treble": 1.6, "loudness": 1.2, "spatial": 0.4, "color": "#DEB887"},

    },

    "🎮 GAMING: COMPETITIVE": {

        "👣 Footsteps Pro":  {"bass": 0.6, "treble": 2.5, "loudness": 1.5, "spatial": 0.8, "color": "#8B4513"},

        "🎯 FPS Focus":      {"bass": 0.8, "treble": 2.2, "loudness": 1.4, "spatial": 0.7, "color": "#556B2F"},

        "🔭 Sniper":         {"bass": 0.9, "treble": 2.5, "loudness": 1.3, "spatial": 0.9, "color": "#2F4F4F"},

        "🏟️ MOBA Arena":     {"bass": 1.5, "treble": 1.5, "loudness": 1.2, "spatial": 0.6, "color": "#483D8B"},

        "🗣️ Voice Chat":     {"bass": 0.5, "treble": 1.8, "loudness": 1.5, "spatial": 0.2, "color": "#20B2AA"},

        "🏃 Speedrun":       {"bass": 1.2, "treble": 1.8, "loudness": 1.4, "spatial": 0.4, "color": "#FFD700"},

        "👂 Sound Whore":    {"bass": 0.5, "treble": 3.0, "loudness": 2.0, "spatial": 1.0, "color": "#DC143C"},

        "🛡️ Strategy":       {"bass": 1.2, "treble": 1.2, "loudness": 1.1, "spatial": 0.5, "color": "#4682B4"},

    },

    "🗡️ GAMING: IMMERSION": {

        "💥 Action RPG":     {"bass": 2.5, "treble": 1.5, "loudness": 1.6, "spatial": 0.6, "color": "#FF4500"},

        "🏎️ Racing Sim":     {"bass": 2.8, "treble": 1.2, "loudness": 1.7, "spatial": 0.5, "color": "#B22222"},

        "👻 Horror":         {"bass": 2.2, "treble": 2.0, "loudness": 1.5, "spatial": 0.9, "color": "#000000"},

        "🌍 Open World":     {"bass": 1.8, "treble": 1.6, "loudness": 1.3, "spatial": 0.8, "color": "#228B22"},

        "🚀 Sci-Fi":         {"bass": 2.0, "treble": 2.2, "loudness": 1.4, "spatial": 0.7, "color": "#00FFFF"},

        "⚔️ War Zone":       {"bass": 3.0, "treble": 1.0, "loudness": 1.8, "spatial": 0.6, "color": "#556B2F"},

        "👾 Retro 8-Bit":    {"bass": 0.8, "treble": 2.5, "loudness": 1.2, "spatial": 0.1, "color": "#32CD32"},

        "🕶️ VR Immersion":   {"bass": 2.0, "treble": 1.8, "loudness": 1.4, "spatial": 1.2, "color": "#9400D3"},

    },

    "✨ VIBE & ATMOSPHERE": {

        "🌃 Night Drive":    {"bass": 2.2, "treble": 1.2, "loudness": 1.3, "spatial": 0.7, "color": "#191970"},

        "🌧️ Rainy Day":      {"bass": 1.4, "treble": 0.8, "loudness": 1.1, "spatial": 0.6, "color": "#708090"},

        "🌴 Tropical":       {"bass": 1.8, "treble": 1.6, "loudness": 1.3, "spatial": 0.7, "color": "#00FF7F"},

        "🌌 Space Walk":     {"bass": 1.5, "treble": 1.5, "loudness": 1.0, "spatial": 1.5, "color": "#4B0082"},

        "☕ Coffee Shop":    {"bass": 1.2, "treble": 1.1, "loudness": 1.0, "spatial": 0.8, "color": "#D2691E"},

        "🏋️ Gym Pump":       {"bass": 3.0, "treble": 1.5, "loudness": 1.8, "spatial": 0.4, "color": "#FF0000"},

        "🛌 Sleepy":         {"bass": 1.5, "treble": 0.5, "loudness": 0.8, "spatial": 0.3, "color": "#483D8B"},

        "🧘 Meditation":     {"bass": 1.3, "treble": 0.7, "loudness": 1.0, "spatial": 1.0, "color": "#E6E6FA"},

        "📚 Study Focus":    {"bass": 1.1, "treble": 1.1, "loudness": 1.0, "spatial": 0.2, "color": "#F5DEB3"},

        "🥳 Party Mode":     {"bass": 2.5, "treble": 1.8, "loudness": 1.8, "spatial": 0.8, "color": "#FF1493"},

        "🚬 Noir Jazz":      {"bass": 1.8, "treble": 1.0, "loudness": 1.2, "spatial": 0.5, "color": "#2F4F4F"},

        "🌅 Sunrise":        {"bass": 1.3, "treble": 1.6, "loudness": 1.2, "spatial": 0.8, "color": "#FFA500"},

    },

    "📻 SIMULATION & FX": {

        "📞 Telephone":      {"bass": 0.1, "treble": 0.5, "loudness": 1.5, "spatial": 0.0, "color": "#696969"},

        "📻 Old Radio":      {"bass": 0.5, "treble": 0.5, "loudness": 1.3, "spatial": 0.1, "color": "#8B4513"},

        "🔊 Cave Echo":      {"bass": 1.5, "treble": 1.5, "loudness": 1.2, "spatial": 2.0, "color": "#778899"},

        "🚿 Bathroom":       {"bass": 1.8, "treble": 1.2, "loudness": 1.3, "spatial": 1.5, "color": "#ADD8E6"},

        "🌊 Underwater":     {"bass": 3.0, "treble": 0.2, "loudness": 1.1, "spatial": 0.8, "color": "#000080"},

        "🏟️ Stadium Live":   {"bass": 2.5, "treble": 1.2, "loudness": 1.6, "spatial": 1.8, "color": "#A52A2A"},

        "📺 TV Speaker":     {"bass": 0.7, "treble": 1.5, "loudness": 1.2, "spatial": 0.1, "color": "#C0C0C0"},

        "🚙 Car Audio":      {"bass": 3.5, "treble": 0.8, "loudness": 1.5, "spatial": 0.3, "color": "#1C1C1C"},

        "📼 VHS Tape":       {"bass": 1.2, "treble": 0.7, "loudness": 1.1, "spatial": 0.2, "color": "#2E8B57"},

        "🚁 Helicopter":     {"bass": 3.0, "treble": 0.5, "loudness": 1.8, "spatial": 0.9, "color": "#556B2F"},

    },

    "🎧 HEADPHONE FIXES": {

        "☀️ Brighten":       {"bass": 1.0, "treble": 1.8, "loudness": 1.1, "spatial": 0.4, "color": "#FFFF00"},

        "🌑 Darken":         {"bass": 1.4, "treble": 0.6, "loudness": 1.1, "spatial": 0.3, "color": "#2F4F4F"},

        "🧱 Remove Mud":     {"bass": 0.7, "treble": 1.3, "loudness": 1.2, "spatial": 0.4, "color": "#DEB887"},

        "🤐 De-Esser":       {"bass": 1.1, "treble": 0.6, "loudness": 1.1, "spatial": 0.3, "color": "#D2B48C"},

        "👐 Widen Stage":    {"bass": 1.1, "treble": 1.2, "loudness": 1.1, "spatial": 1.2, "color": "#E0FFFF"},

        "🎯 Center Image":   {"bass": 1.1, "treble": 1.1, "loudness": 1.1, "spatial": -0.2, "color": "#A9A9A9"},

        "📱 Phone Speaker":  {"bass": 0.2, "treble": 2.0, "loudness": 1.8, "spatial": 0.1, "color": "#DCDCDC"},

        "💻 Laptop Boost":   {"bass": 2.0, "treble": 1.0, "loudness": 1.5, "spatial": 0.2, "color": "#C0C0C0"},

    },

    "🗣️ VOICE & CINEMA": {

        "🎧 Podcast":        {"bass": 0.9, "treble": 1.4, "loudness": 1.5, "spatial": 0.2, "color": "#20B2AA"},

        "🗣️ Vocal Boost":    {"bass": 0.8, "treble": 1.8, "loudness": 1.4, "spatial": 0.3, "color": "#FF69B4"},

        "🎬 Cinema Action":  {"bass": 2.5, "treble": 1.4, "loudness": 1.6, "spatial": 0.8, "color": "#8B0000"},

        "💬 Dialogue":       {"bass": 0.8, "treble": 1.5, "loudness": 1.4, "spatial": 0.2, "color": "#F0E68C"},

        "🍿 Movie Night":    {"bass": 2.0, "treble": 1.2, "loudness": 1.3, "spatial": 0.7, "color": "#B22222"},

        "💣 Explosions":     {"bass": 4.0, "treble": 0.8, "loudness": 1.8, "spatial": 0.6, "color": "#FF4500"},

        "👂 ASMR":           {"bass": 1.1, "treble": 1.8, "loudness": 1.5, "spatial": 0.9, "color": "#FFC0CB"},

        "📰 News Anchor":    {"bass": 1.2, "treble": 1.3, "loudness": 1.4, "spatial": 0.1, "color": "#708090"},

    }

}

# ========================= AUDIO ENGINE =========================



class AudioProcessor:

    def __init__(self, sample_rate, block_size):

        self.sample_rate = sample_rate

        self.block_size = block_size

        self.preset = {"bass": 1.0, "treble": 1.0, "loudness": 1.0, "spatial": 0.0}

        self.master_volume = 1.0

       

        # 8D State

        self.phase = 0.0

        self.input_level = 0.0

        self.output_level = 0.0

       

        # FFT Setup

        self.freqs = np.fft.rfftfreq(block_size, 1.0 / sample_rate)

        self.bass_indices = np.where(self.freqs < 250)[0]

        self.treble_indices = np.where(self.freqs > 4000)[0]



    def set_preset(self, params):

        self.preset = params.copy()



    def set_volume(self, volume):

        self.master_volume = max(0.0, min(2.0, volume))



    def process(self, indata):

        try:

            if indata is None: return np.zeros((self.block_size, 2), dtype=np.float32)

           

            # Stereo handling

            if indata.ndim == 1: audio = np.column_stack((indata, indata))

            elif indata.shape[1] == 1: audio = np.column_stack((indata[:, 0], indata[:, 0]))

            else: audio = indata



            # Input Meter

            self.input_level = np.max(np.abs(audio[:100])) * 2.0

           

            # Params

            bass = self.preset.get("bass", 1.0)

            treble = self.preset.get("treble", 1.0)

            loud = self.preset.get("loudness", 1.0)

            spatial = self.preset.get("spatial", 0.0)

            pan_depth = self.preset.get("pan_depth", 0.0)

            pan_speed = self.preset.get("pan_speed", 0.0)

           

            # FFT EQ

            if abs(bass - 1.0) > 0.01 or abs(treble - 1.0) > 0.01:

                l_fft = np.fft.rfft(audio[:, 0])

                if bass != 1.0: l_fft[self.bass_indices] *= bass

                if treble != 1.0: l_fft[self.treble_indices] *= treble

                l_out = np.fft.irfft(l_fft, n=self.block_size)

               

                r_fft = np.fft.rfft(audio[:, 1])

                if bass != 1.0: r_fft[self.bass_indices] *= bass

                if treble != 1.0: r_fft[self.treble_indices] *= treble

                r_out = np.fft.irfft(r_fft, n=self.block_size)

               

                out = np.column_stack((l_out, r_out))

            else:

                out = audio.copy()



            out *= loud



            # 8D Logic

            if pan_depth > 0.01:

                n_samples = len(out)

                t = np.arange(n_samples) / self.sample_rate

                lfo_phase = self.phase + 2 * np.pi * pan_speed * t

                self.phase = lfo_phase[-1] % (2 * np.pi)

                pan = np.sin(lfo_phase) * pan_depth

                theta = (pan + 1.0) * (np.pi / 4.0)

                out[:, 0] *= np.cos(theta)

                out[:, 1] *= np.sin(theta)



            # Spatial

            if abs(spatial) > 0.01:

                mid = (out[:, 0] + out[:, 1]) * 0.5

                side = (out[:, 0] - out[:, 1]) * 0.5

                side *= (1.0 + spatial)

                out[:, 0] = mid + side

                out[:, 1] = mid - side



            out *= self.master_volume

            np.tanh(out, out=out) # Soft clip

           

            self.output_level = np.max(np.abs(out[:100])) * 2.0

            return out.astype(np.float32)



        except Exception:

            return indata



class AudioThread(QThread):

    status_signal = pyqtSignal(str)

    error_signal = pyqtSignal(str)



    def __init__(self, processor, input_idx, output_idx, sample_rate, buffer_mode):

        super().__init__()

        self.processor = processor

        self.input_idx = input_idx

        self.output_idx = output_idx

        self.sample_rate = sample_rate

        self.buffer_mode = buffer_mode

        self.running = False



    def run(self):

        self.running = True

        bs = 8192 if self.buffer_mode == "stable" else 4096

        lat = 0.2 if self.buffer_mode == "stable" else 0.1

       

        self.processor.block_size = bs

        # Re-init FFT bins for new blocksize

        self.processor.freqs = np.fft.rfftfreq(bs, 1.0 / self.sample_rate)

        self.processor.bass_indices = np.where(self.processor.freqs < 250)[0]

        self.processor.treble_indices = np.where(self.processor.freqs > 4000)[0]



        try:

            with sd.Stream(

                device=(self.input_idx, self.output_idx),

                samplerate=self.sample_rate,

                blocksize=bs,

                dtype=np.float32,

                channels=2,

                latency=lat,

                callback=self.audio_callback

            ):

                self.status_signal.emit(f"ONLINE | {self.sample_rate}Hz")

                while self.running:

                    self.msleep(100)

        except Exception as e:

            self.error_signal.emit(str(e))

       

        self.status_signal.emit("OFFLINE")



    def audio_callback(self, indata, outdata, frames, time, status):

        if status: outdata.fill(0); return

        try:

            result = self.processor.process(indata)

            n = min(len(result), len(outdata))

            outdata[:n] = result[:n]

            if n < len(outdata): outdata[n:] = 0

        except:

            outdata.fill(0)



    def stop(self):

        self.running = False

        self.wait(1000)



# ========================= SCI-FI VISUALIZER =========================



class SciFiReactor(QWidget):

    def __init__(self):

        super().__init__()

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.setMinimumSize(300, 300)

        self.audio_level = 0.0

        self.angle_1 = 0

        self.angle_2 = 180

        self.angle_3 = 90

       

        # Animation loop

        self.timer = QTimer(self)

        self.timer.timeout.connect(self.animate)

        self.timer.start(16) # ~60 FPS



    def set_level(self, level):

        # Smooth attack, fast decay

        target = level

        if target > self.audio_level:

            self.audio_level = self.audio_level * 0.7 + target * 0.3

        else:

            self.audio_level = self.audio_level * 0.9 + target * 0.1



    def animate(self):

        # Rotation speed based on audio intensity

        speed = 2 + (self.audio_level * 15)

        self.angle_1 = (self.angle_1 + speed) % 360

        self.angle_2 = (self.angle_2 - (speed * 0.7)) % 360

        self.angle_3 = (self.angle_3 + (speed * 0.3)) % 360

        self.update()



    def paintEvent(self, e):

        p = QPainter(self)

        p.setRenderHint(QPainter.RenderHint.Antialiasing)

       

        w, h = self.width(), self.height()

        center = QPointF(w/2, h/2)

        base_size = min(w, h) * 0.35

       

        # Audio reactive pulse size

        pulse = base_size * (1 + (self.audio_level * 0.5))

       

        # 1. Background Glow

        grad = QRadialGradient(center, base_size * 2)

        grad.setColorAt(0, QColor(0, 255, 200, 40))

        grad.setColorAt(1, QColor(0, 0, 0, 0))

        p.fillRect(self.rect(), Qt.BrushStyle.NoBrush) # Clear

        p.setBrush(grad)

        p.setPen(Qt.PenStyle.NoPen)

        p.drawEllipse(center, base_size*2, base_size*2)



        # 2. Outer Rotating Ring (Tech HUD style)

        pen = QPen(QColor("#00ffcc"))

        pen.setWidth(3)

        p.setPen(pen)

        p.setBrush(Qt.BrushStyle.NoBrush)

       

        rect_outer = QRectF(center.x() - pulse, center.y() - pulse, pulse*2, pulse*2)

        p.drawArc(rect_outer, int(self.angle_1 * 16), 100 * 16)

        p.drawArc(rect_outer, int((self.angle_1 + 180) * 16), 100 * 16)

       

        # 3. Inner Rotating Ring

        pen.setColor(QColor("#ff00cc"))

        pen.setWidth(2)

        p.setPen(pen)

        pulse_inner = pulse * 0.8

        rect_inner = QRectF(center.x() - pulse_inner, center.y() - pulse_inner, pulse_inner*2, pulse_inner*2)

        p.drawArc(rect_inner, int(self.angle_2 * 16), 240 * 16)

       

        # 4. Center Core

        core_rad = pulse * 0.5

        core_grad = QRadialGradient(center, core_rad)

        # Change core color based on intensity

        if self.audio_level > 0.5:

            core_grad.setColorAt(0, QColor("#ffaa00")) # Warning orange/red

            core_grad.setColorAt(1, QColor("#550000"))

        else:

            core_grad.setColorAt(0, QColor("#ffffff"))

            core_grad.setColorAt(0.3, QColor("#00ccff"))

            core_grad.setColorAt(1, QColor("#002233"))

           

        p.setBrush(core_grad)

        p.setPen(Qt.PenStyle.NoPen)

        p.drawEllipse(center, core_rad, core_rad)

       

        # 5. Triangle Spin

        p.save()

        p.translate(center)

        p.rotate(self.angle_3)

        poly = QPolygonF([QPointF(0, -core_rad*0.6), QPointF(core_rad*0.5, core_rad*0.3), QPointF(-core_rad*0.5, core_rad*0.3)])

        p.setBrush(QColor(255, 255, 255, 100))

        p.drawPolygon(poly)

        p.restore()





# ========================= CUSTOM UI COMPONENTS =========================



class ModernButton(QPushButton):

    def __init__(self, text, is_primary=False):

        super().__init__(text)

        self.setFixedHeight(40)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.is_primary = is_primary

        self.set_style()



    def set_style(self):

        if self.is_primary:

            self.setStyleSheet("""

                QPushButton {

                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #009977, stop:1 #00cc88);

                    color: white; border: none; border-radius: 5px; font-weight: bold; font-size: 13px;

                }

                QPushButton:hover { background: #00ffaa; }

                QPushButton:pressed { background: #007755; }

            """)

        else:

            self.setStyleSheet("""

                QPushButton {

                    background: #2a2a3a; color: #ccc; border: 1px solid #444;

                    border-radius: 5px; font-size: 12px;

                }

                QPushButton:hover { border: 1px solid #00ffcc; color: white; background: #333; }

                QPushButton:checked { background: #00ffcc; color: black; border: none; font-weight: bold;}

            """)



# ========================= MAIN WINDOW =========================



class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("⚡ NEURO-AUDIO CORE")

        self.resize(1100, 700)

        self.setStyleSheet("""

            QMainWindow { background-color: #0b0f19; }

            QLabel { color: #8899aa; font-family: 'Segoe UI'; }

            QComboBox {

                background: #1a1f2e; color: #00ffcc; border: 1px solid #334455;

                padding: 5px; border-radius: 4px;

            }

            QGroupBox {

                border: 1px solid #334455; border-radius: 8px; margin-top: 20px;

                font-weight: bold; color: #00ffcc;

            }

            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }

            QSlider::groove:horizontal { height: 6px; background: #222; border-radius: 3px; }

            QSlider::handle:horizontal { width: 16px; margin: -5px 0; border-radius: 8px; background: #00ffcc; }

            QSlider::sub-page:horizontal { background: #008866; border-radius: 3px; }

        """)

       

        self.processor = None

        self.thread = None

        self.device_pairs = []

        self.active_preset_btn = None

       

        self.init_ui()

        self.scan_devices()

       

        # Audio Link Timer

        self.sync_timer = QTimer()

        self.sync_timer.timeout.connect(self.sync_ui)

        self.sync_timer.start(30) # 30ms updates



    def init_ui(self):

        main_widget = QWidget()

        self.setCentralWidget(main_widget)

       

        # Main Layout: 3 Columns [ Controls | Visualizer | Presets ]

        main_layout = QHBoxLayout(main_widget)

        main_layout.setContentsMargins(20, 20, 20, 20)

        main_layout.setSpacing(20)

       

        # --- LEFT COLUMN: CONTROLS ---

        left_panel = QFrame()

        left_panel.setFixedWidth(320)

        left_panel.setStyleSheet("background: #111625; border-radius: 15px; border: 1px solid #223344;")

        left_layout = QVBoxLayout(left_panel)

       

        # Title

        title = QLabel("NEURO CORE")

        title.setStyleSheet("font-size: 26px; font-weight: 900; color: white; letter-spacing: 2px;")

        subtitle = QLabel("HOLOGRAPHIC AUDIO ENGINE")

        subtitle.setStyleSheet("font-size: 10px; color: #00ffcc; letter-spacing: 4px; margin-bottom: 20px;")

        left_layout.addWidget(title)

        left_layout.addWidget(subtitle)

       

        # System Status

        self.lbl_status = QLabel("SYSTEM OFFLINE")

        self.lbl_status.setStyleSheet("background: #220000; color: #ff5555; padding: 8px; border-radius: 4px; font-weight: bold; text-align: center;")

        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        left_layout.addWidget(self.lbl_status)

       

        # Device Selection

        left_layout.addWidget(QLabel("INPUT / OUTPUT CHAIN"))

        self.combo_dev = QComboBox()

        left_layout.addWidget(self.combo_dev)

       

        btn_refresh = ModernButton("Scan Devices")

        btn_refresh.clicked.connect(self.scan_devices)

        left_layout.addWidget(btn_refresh)

       

        # Latency Mode

        g_mode = QGroupBox("LATENCY MODE")

        v_mode = QVBoxLayout(g_mode)

        self.btn_stable = QRadioButton("STABLE (Fix Glitches)")

        self.btn_fast = QRadioButton("FAST (Low Latency)")

        self.btn_stable.setChecked(True)

        self.btn_stable.setStyleSheet("color: white;")

        self.btn_fast.setStyleSheet("color: white;")

        v_mode.addWidget(self.btn_stable)

        v_mode.addWidget(self.btn_fast)

        left_layout.addWidget(g_mode)

       

        # Volume

        left_layout.addSpacing(20)

        left_layout.addWidget(QLabel("MASTER GAIN"))

        self.slider_vol = QSlider(Qt.Orientation.Horizontal)

        self.slider_vol.setRange(0, 200)

        self.slider_vol.setValue(100)

        self.slider_vol.valueChanged.connect(self.update_volume)

        left_layout.addWidget(self.slider_vol)

       

        left_layout.addStretch()

       

        # Power Button

        self.btn_power = ModernButton("INITIALIZE CORE", is_primary=True)

        self.btn_power.setFixedHeight(60)

        self.btn_power.setStyleSheet(self.btn_power.styleSheet() + "font-size: 16px;")

        self.btn_power.clicked.connect(self.toggle_power)

        left_layout.addWidget(self.btn_power)

       

        main_layout.addWidget(left_panel)

       

        # --- CENTER COLUMN: VISUALIZER ---

        center_panel = QFrame()

        center_panel.setStyleSheet("background: transparent;")

        c_layout = QVBoxLayout(center_panel)

       

        self.visualizer = SciFiReactor()

        c_layout.addWidget(self.visualizer)

       

        # Mini meters below

        meter_layout = QHBoxLayout()

        self.lbl_in_meter = QLabel("IN: -Inf dB")

        self.lbl_out_meter = QLabel("OUT: -Inf dB")

        meter_layout.addWidget(self.lbl_in_meter)

        meter_layout.addStretch()

        meter_layout.addWidget(self.lbl_out_meter)

        c_layout.addLayout(meter_layout)

       

        main_layout.addWidget(center_panel, stretch=1)

       

        # --- RIGHT COLUMN: PRESETS ---

        right_panel = QFrame()

        right_panel.setFixedWidth(280)

        right_panel.setStyleSheet("background: #111625; border-radius: 15px; border: 1px solid #223344;")

        r_layout = QVBoxLayout(right_panel)

        r_layout.addWidget(QLabel("SOUND SIGNATURES"))

       

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setStyleSheet("background: transparent; border: none;")

       

        p_widget = QWidget()

        p_layout = QVBoxLayout(p_widget)

       

        for category, presets in PRESETS.items():

            grp = QGroupBox(category)

            g_layout = QGridLayout(grp)

            g_layout.setSpacing(8)

           

            row, col = 0, 0

            for name, params in presets.items():

                # Extract emoji and name

                parts = name.split(" ", 1)

                short_name = parts[1] if len(parts) > 1 else name

                emoji = parts[0]

               

                btn = ModernButton(f"{emoji} {short_name}")

                btn.setCheckable(True)

                btn.clicked.connect(lambda checked, n=name, p=params, b=btn: self.apply_preset(n, p, b))

                g_layout.addWidget(btn, row, col)

               

                col += 1

                if col > 1:

                    col = 0

                    row += 1

           

            p_layout.addWidget(grp)

           

        p_layout.addStretch()

        scroll.setWidget(p_widget)

        r_layout.addWidget(scroll)

       

        main_layout.addWidget(right_panel)



    def scan_devices(self):

        self.combo_dev.clear()

        self.device_pairs = []

        if not AUDIO_AVAILABLE: return

       

        try:

            devs = sd.query_devices()

            apis = sd.query_hostapis()

           

            # Smart filtering for loopback free input/output pairs

            valid_inputs = [i for i, d in enumerate(devs) if d['max_input_channels'] > 0]

            valid_outputs = [i for i, d in enumerate(devs) if d['max_output_channels'] > 0]

           

            for i_idx in valid_inputs:

                for o_idx in valid_outputs:

                    i_d = devs[i_idx]

                    o_d = devs[o_idx]

                   

                    if i_d['hostapi'] != o_d['hostapi']: continue

                    if int(i_d['default_samplerate']) != int(o_d['default_samplerate']): continue

                    if i_idx == o_idx: continue

                   

                    api_name = apis[i_d['hostapi']]['name']

                    # Clean up names

                    in_name = i_d['name'][:20]

                    out_name = o_d['name'][:20]

                   

                    display = f"[{api_name}] {in_name}...  ➜  {out_name}..."

                   

                    self.device_pairs.append({

                        'in': i_idx, 'out': o_idx, 'rate': int(i_d['default_samplerate']),

                        'api': api_name

                    })

                    self.combo_dev.addItem(display)

           

            # Prioritize WASAPI

            if self.combo_dev.count() > 0:

                self.combo_dev.setCurrentIndex(0)

               

        except Exception as e:

            self.combo_dev.addItem(f"Error: {e}")



    def toggle_power(self):

        if self.thread and self.thread.isRunning():

            self.thread.stop()

            self.thread = None

            self.btn_power.setText("INITIALIZE CORE")

            self.btn_power.setStyleSheet("""

                QPushButton {

                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #009977, stop:1 #00cc88);

                    color: white; border: none; border-radius: 5px; font-weight: bold; font-size: 16px;

                }

                QPushButton:hover { background: #00ffaa; }

            """)

            self.lbl_status.setText("SYSTEM OFFLINE")

            self.lbl_status.setStyleSheet("background: #220000; color: #ff5555; padding: 8px; border-radius: 4px; font-weight: bold;")

            self.visualizer.set_level(0)

        else:

            idx = self.combo_dev.currentIndex()

            if idx < 0: return

           

            cfg = self.device_pairs[idx]

            mode = "stable" if self.btn_stable.isChecked() else "fast"

           

            self.processor = AudioProcessor(cfg['rate'], 4096)

            self.processor.set_volume(self.slider_vol.value() / 100.0)

           

            # Re-apply preset if one was selected

            if self.active_preset_btn:

                self.active_preset_btn.click()

           

            self.thread = AudioThread(self.processor, cfg['in'], cfg['out'], cfg['rate'], mode)

            self.thread.status_signal.connect(lambda s: self.lbl_status.setText(s))

            self.thread.error_signal.connect(lambda e: QMessageBox.critical(self, "Core Error", e))

            self.thread.start()

           

            self.btn_power.setText("TERMINATE PROCESS")

            self.btn_power.setStyleSheet("""

                QPushButton { background: #550000; color: white; border: 1px solid #ff0000; border-radius: 5px; font-weight: bold; font-size: 16px; }

                QPushButton:hover { background: #770000; }

            """)

            self.lbl_status.setStyleSheet("background: #002211; color: #00ff88; padding: 8px; border-radius: 4px; font-weight: bold;")



    def apply_preset(self, name, params, btn):

        if self.active_preset_btn:

            self.active_preset_btn.setChecked(False)

       

        self.active_preset_btn = btn

        btn.setChecked(True)

       

        if self.processor:

            self.processor.set_preset(params)



    def update_volume(self, val):

        if self.processor:

            self.processor.set_volume(val / 100.0)



    def sync_ui(self):

        if self.processor and self.thread and self.thread.isRunning():

            # Get audio level for visualizer (normalized roughly 0.0 to 1.0)

            lvl = min(1.0, self.processor.output_level * 1.5)

            self.visualizer.set_level(lvl)

           

            self.lbl_in_meter.setText(f"IN: {self.processor.input_level*100:.1f}%")

            self.lbl_out_meter.setText(f"OUT: {self.processor.output_level*100:.1f}%")

        else:

            self.visualizer.set_level(0)





if __name__ == "__main__":

    app = QApplication(sys.argv)

   

    # Set app font

    font = QFont("Segoe UI", 9)

    app.setFont(font)

   

    window = MainWindow()

    window.show()

    sys.exit(app.exec())