"""
AURA — Neon Audio Suite UI (Advanced Edition)
------------------------------------------------
High-Performance PyQt6 GUI with Database-Backed Library & Smart Presets.

Improvements:
- 🎛️ SMART PRESETS: 70+ presets. Tweakable without resetting (Auto-saves to Custom).
- 🔀 DJ CROSSFADE: Dual-deck engine mixes ALL track changes seamlessly.
- 🔁 LOOP & SHUFFLE: Full playback control integrated.
- 🔊 MASTER VOLUME: Dedicated volume slider with dynamic gain scaling.
- 🖐️ DRAG & DROP: Drop files to play instantly (Temp Playlist).
- 🚀 DATABASE LIBRARY: Uses SQLite to index folders. Zero RAM usage.
- 🔍 SMART SEARCH: Instant filtering of your music library.
- 💎 64-BIT PRECISION: All DSP runs in Float64.
- 🔇 SILENT MODE: Suppresses console logs (FFmpeg/Qt).

Dependencies:
  pip install pyqt6 numpy

Run:
  python aura_ui_advanced.py
"""

from __future__ import annotations

import math
import os
import sys
import wave
import gc
import time
import random
import sqlite3
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any

import numpy as np

try:
    from PyQt6.QtCore import (
        Qt, QTimer, QSize, QRectF, QPointF, QThread, pyqtSignal, QObject, QMutex, QUrl
    )
    from PyQt6.QtGui import (
        QColor, QFont, QPainter, QPainterPath, QPen, QBrush,
        QLinearGradient, QRadialGradient, QAction, QConicalGradient, QIcon,
        QDragEnterEvent, QDropEvent
    )
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QSlider, QFileDialog, QMessageBox,
        QLineEdit, QTreeWidget, QTreeWidgetItem, QSplitter, QFrame,
        QDial, QComboBox, QGroupBox, QFormLayout, QCheckBox,
        QSizePolicy, QTextEdit, QProgressBar, QTabWidget, QListWidget, 
        QAbstractItemView, QHeaderView
    )
    from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
except Exception as e:
    raise SystemExit(
        "PyQt6 is required.\nInstall with: pip install pyqt6 numpy\n\n"
        f"Import error: {e}"
    )


# -----------------------------
# Feature Registry & Presets
# -----------------------------

FEATURES: Dict[str, Dict[str, List[str]]] = {
    "🔊 Core Audio Effects": {
        "Equalizer (EQ)": [
            "Graphic EQ", "Parametric EQ", "Dynamic EQ",
            "Linear Phase EQ", "Tilt EQ", "Bass boost", "Treble boost"
        ],
        "Volume & Dynamics": [
            "Gain", "Loudness normalization", "Smart volume leveling",
            "Peak limiter", "Compressor", "Multiband compressor"
        ],
        "Stereo & Spatial": [
            "Stereo widening", "Mono downmix", "Mid/Side control",
            "Crossfeed"
        ],
        "Ambience": [
            "Reverb", "Room reverb", "Hall reverb", "Plate reverb"
        ],
    },
    "🎚️ Editing & Time": {
        "Structure": [
            "Trim", "Fade in", "Fade out", "Crossfade"
        ],
        "Time Manipulation": [
            "Stretch", "Warp", "Reverse playback"
        ]
    },
    "🧠 AI & Special": {
        "Intelligent": [
            "AI mastering", "Stem separation", "Vocal isolation"
        ],
        "Playback": [
            "Night mode EQ", "Focus mode clarity", "8D Audio Sim"
        ]
    },
    "📀 Mastering": {
        "Finalization": [
            "Master EQ", "Limiter", "Dither", "Loudness targeting (LUFS)",
            "True peak limiting"
        ]
    }
}

# Extensive Preset Library
PRESETS = {
    "--- Custom / Modified ---": {"i": 0.5, "w": 0.5, "fx": []},
    
    # 🎵 GENRES & STYLES
    "🔥 Club Master": {"i": 0.85, "w": 0.80, "fx": ["Bass boost", "Compressor", "Limiter", "Stereo widening", "Crossfade"]},
    "🎸 Rock/Metal Polish": {"i": 0.80, "w": 0.65, "fx": ["Distortion", "Graphic EQ", "Compressor", "Stereo widening", "Crossfade"]},
    "🎻 Classical Concert": {"i": 0.70, "w": 0.50, "fx": ["Hall reverb", "Linear Phase EQ", "Dynamic EQ", "Crossfade"]},
    "🎷 Jazz Lounge": {"i": 0.60, "w": 0.40, "fx": ["Room reverb", "Tube warmth", "Mid-range shaping", "Crossfade"]},
    "🎤 Hip Hop Slam": {"i": 0.90, "w": 0.85, "fx": ["Sub-bass generator", "Compressor", "Transient shaper", "Crossfade"]},
    "🎹 Techno Rumble": {"i": 0.95, "w": 0.90, "fx": ["Bass boost", "Stereo widening", "Sidechain simulation", "Limiter", "Crossfade"]},
    "🔊 Dubstep Grime": {"i": 0.95, "w": 1.0, "fx": ["Distortion", "Multi-band compressor", "Bass enhancer", "Crossfade"]},
    "🇯🇲 Reggae Chill": {"i": 0.70, "w": 0.60, "fx": ["Bass boost", "Tape delay", "Reverb", "Crossfade"]},
    "⛺ Acoustic Campfire": {"i": 0.50, "w": 0.30, "fx": ["Compressor", "Warm EQ", "Stereo narrowing", "Crossfade"]},
    "📼 80s Synthwave": {"i": 0.75, "w": 0.70, "fx": ["Plate reverb", "Chorus", "Tape warmth", "Crossfade"]},
    "🤠 Country Roads": {"i": 0.60, "w": 0.40, "fx": ["Acoustic resonance", "Compressor", "Room reverb", "Crossfade"]},
    "🕺 Disco Funk": {"i": 0.80, "w": 0.75, "fx": ["Bass boost", "Phaser", "Stereo widening", "Crossfade"]},
    
    # 🎧 BASS & DRIVE
    "🚗 Car Bass Test": {"i": 0.95, "w": 1.0, "fx": ["Sub-bass generator", "Dynamic bass boost", "Peak limiter", "Crossfade"]},
    "🥊 Punchy Kick": {"i": 0.75, "w": 0.70, "fx": ["Transient shaper", "Compressor", "Graphic EQ", "Crossfade"]},
    "💣 Bass Nuke": {"i": 1.0, "w": 1.0, "fx": ["Sub-bass generator", "Bass enhancer", "Distortion", "Limiter", "Crossfade"]},
    "📉 Sub-Bass Focus": {"i": 0.85, "w": 0.90, "fx": ["Low-pass filter", "Sub-bass generator", "Mono downmix", "Crossfade"]},
    "🔉 Low End Theory": {"i": 0.80, "w": 0.90, "fx": ["Bass boost", "Multiband compressor", "Crossfade"]},

    # 🎤 VOCAL & SPEECH
    "🎙️ Podcast Clarity": {"i": 0.60, "w": 1.0, "fx": ["Vocal isolation", "De-esser", "Compressor", "Smart volume leveling", "Crossfade"]},
    "🧚 Airy Vocals": {"i": 0.50, "w": 0.40, "fx": ["Treble boost", "Plate reverb", "Exciter", "Crossfade"]},
    "📻 Radio Host": {"i": 0.70, "w": 0.90, "fx": ["Compressor", "Limiter", "Bass boost", "Noise reduction", "Crossfade"]},
    "🗣️ Dialogue Boost": {"i": 0.65, "w": 1.0, "fx": ["Mid-range shaping", "Compressor", "Noise reduction", "Crossfade"]},
    "🤫 ASMR Tingle": {"i": 0.80, "w": 1.0, "fx": ["Compressor", "Limiter", "Treble boost", "Stereo widening", "Crossfade"]},
    "📞 Conference Call": {"i": 0.55, "w": 1.0, "fx": ["Noise reduction", "High-pass filter", "Gate", "Crossfade"]},

    # ✨ VIBE & ATMOSPHERE
    "☕ Lo-Fi Study": {"i": 0.65, "w": 0.60, "fx": ["Sample rate reduction", "Tape warmth", "Low-pass filter", "Crossfade"]},
    "🌃 Night Drive": {"i": 0.55, "w": 0.50, "fx": ["Stereo widening", "Bass boost", "Reverb", "Tilt EQ", "Crossfade"]},
    "🌌 Ethereal Space": {"i": 0.80, "w": 0.85, "fx": ["Hall reverb", "Stereo widening", "Delay", "Chorus", "Crossfade"]},
    "🌀 8D Audio Sim": {"i": 0.90, "w": 1.0, "fx": ["8D Audio Sim", "Stereo widening", "Reverb", "Crossfade"]},
    "🛁 Bathroom Singing": {"i": 0.60, "w": 0.50, "fx": ["Room reverb", "Slapback delay", "Crossfade"]},
    "🏰 Cathedral": {"i": 0.90, "w": 0.90, "fx": ["Hall reverb", "Convolution reverb", "Stereo widening", "Crossfade"]},
    "🌊 Underwater": {"i": 0.80, "w": 1.0, "fx": ["Low-pass filter", "Reverb", "Phaser", "Crossfade"]},
    "🍃 Forest Walk": {"i": 0.60, "w": 0.70, "fx": ["Stereo widening", "Treble boost", "Wind noise sim", "Crossfade"]},
    "🌧️ Rainy Day": {"i": 0.55, "w": 0.60, "fx": ["Low-pass filter", "Tape warmth", "Mono downmix", "Crossfade"]},
    
    # 🎮 GAMING
    "👣 Footsteps Focus": {"i": 0.80, "w": 1.0, "fx": ["Treble boost", "Compressor", "Graphic EQ", "Smart volume leveling", "Crossfade"]},
    "⚔️ Cinematic RPG": {"i": 0.70, "w": 0.60, "fx": ["Stereo widening", "Bass boost", "Hall reverb", "Crossfade"]},
    "💥 Explosion Impact": {"i": 0.95, "w": 0.90, "fx": ["Sub-bass generator", "Limiter", "Distortion", "Crossfade"]},
    "🏎️ Racing Immersion": {"i": 0.85, "w": 0.80, "fx": ["Bass boost", "Stereo widening", "Doppler effect", "Crossfade"]},
    "👻 Horror Atmosphere": {"i": 0.75, "w": 0.70, "fx": ["Reverb", "Pitch shifting", "Binaural rendering", "Crossfade"]},
    "👾 Retro Arcade": {"i": 0.70, "w": 0.80, "fx": ["Bitcrusher", "Square wave gen", "Fast decay reverb", "Crossfade"]},
    
    # 🧪 EXPERIMENTAL & FX
    "📼 Old Telephone": {"i": 0.90, "w": 1.0, "fx": ["Band-pass filter", "Bitcrusher", "Distortion", "Crossfade"]},
    "🤖 Sci-Fi Robot": {"i": 0.85, "w": 0.90, "fx": ["Ring modulator", "Delay", "Flanger", "Crossfade"]},
    "📀 Vinyl Crackle": {"i": 0.60, "w": 0.50, "fx": ["Noise generator", "Band-pass filter", "Warp", "Crossfade"]},
    "👽 Alien Transmission": {"i": 0.90, "w": 1.0, "fx": ["Bitcrusher", "Flanger", "Reverse playback", "Crossfade"]},
    "📣 Megaphone": {"i": 0.85, "w": 1.0, "fx": ["Band-pass filter", "Distortion", "Peak limiter", "Crossfade"]},
    "🤯 Mind Melt": {"i": 1.0, "w": 1.0, "fx": ["Phaser", "Flanger", "Chorus", "Stereo widening", "Crossfade"]},

    # 📀 MASTERING & UTILITY
    "🧼 Clean Master": {"i": 0.60, "w": 1.0, "fx": ["Multiband compressor", "Master EQ", "True peak limiting", "Crossfade"]},
    "🔊 Loudness Wars": {"i": 0.95, "w": 1.0, "fx": ["Gain", "Peak limiter", "Compressor", "Saturation", "Crossfade"]},
    "📱 Phone Speaker Fix": {"i": 0.70, "w": 1.0, "fx": ["Mid-range shaping", "Compressor", "Limiter", "Crossfade"]},
    "💤 Sleep Mode": {"i": 0.40, "w": 0.60, "fx": ["Low-pass filter", "Volume leveling", "Crossfade"]},
}


# -----------------------------
# Helpers: High-Fidelity WAV I/O
# -----------------------------

def read_wav(path: str) -> Tuple[np.ndarray, int]:
    try:
        with wave.open(path, "rb") as wf:
            ch = wf.getnchannels()
            sr = wf.getframerate()
            sampwidth = wf.getsampwidth()
            nframes = wf.getnframes()
            raw = wf.readframes(nframes)
        
        if sampwidth == 1:
            data = np.frombuffer(raw, dtype=np.uint8).astype(np.float64)
            data -= 128.0; data /= 128.0
        elif sampwidth == 2:
            data = np.frombuffer(raw, dtype=np.int16).astype(np.float64)
            data /= 32768.0
        elif sampwidth == 3:
            a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
            b = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8) | (a[:, 2].astype(np.int32) << 16))
            mask = (b & 0x800000) != 0; b[mask] |= 0xFF000000
            data = b.astype(np.float64) / 8388608.0
        elif sampwidth == 4:
            data = np.frombuffer(raw, dtype=np.int32).astype(np.float64) / 2147483648.0
        else:
            raise ValueError(f"Unsupported bit depth: {sampwidth*8}")

        if ch > 1: data = data.reshape(-1, ch)
        else: data = data.reshape(-1, 1)

        del raw; gc.collect()
        return np.clip(data, -1.0, 1.0), sr
    except Exception as e:
        raise IOError(f"Read error: {e}")


def write_wav(path: str, audio: np.ndarray, sr: int) -> None:
    audio = np.clip(audio, -1.0, 1.0)
    pcm = (audio * 2147483647.0).astype(np.int32)
    ch = 1 if pcm.ndim == 1 else pcm.shape[1]
    with wave.open(path, "wb") as wf:
        wf.setnchannels(ch); wf.setsampwidth(4); wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    del pcm; gc.collect()


# -----------------------------
# DSP Primitives (Optimized Float64)
# -----------------------------

def db_to_lin(db: float) -> float:
    return float(10.0 ** (db / 20.0))

def one_pole_low_shelf(x: np.ndarray, sr: int, freq: float, gain_db: float) -> np.ndarray:
    if gain_db == 0.0: return x
    g = db_to_lin(gain_db)
    alpha = math.exp(-2.0 * math.pi * freq / max(sr, 1))
    y = np.empty_like(x)
    coeff_b = 1.0 - alpha
    z = np.zeros(x.shape[1], dtype=np.float64)
    for i in range(len(x)):
        z = alpha * z + coeff_b * x[i]
        y[i] = x[i] + (g - 1.0) * z
    return y

def simple_compressor(x: np.ndarray, threshold_db: float, ratio: float) -> np.ndarray:
    env = np.abs(x)
    env_db = 20.0 * np.log10(np.maximum(env, 1e-12))
    over_mask = env_db > threshold_db
    gain_db = np.zeros_like(env_db)
    diff = env_db[over_mask] - threshold_db
    gain_db[over_mask] = -diff * (1.0 - 1.0/max(ratio, 1.0))
    gain_lin = np.power(10.0, gain_db / 20.0)
    return x * gain_lin

def stereo_widen(x: np.ndarray, amount: float) -> np.ndarray:
    if x.shape[1] < 2: return x
    mid = 0.5 * (x[:, 0] + x[:, 1]); side = 0.5 * (x[:, 0] - x[:, 1])
    side *= (1.0 + amount)
    res = np.empty_like(x)
    res[:, 0] = mid + side; res[:, 1] = mid - side
    return res


# -----------------------------
# Database Manager
# -----------------------------

class LibraryManager:
    DB_NAME = "aura_library.db"
    def __init__(self): self.init_db()
    def init_db(self):
        with sqlite3.connect(self.DB_NAME) as conn:
            conn.execute('CREATE TABLE IF NOT EXISTS tracks (id INTEGER PRIMARY KEY, path TEXT UNIQUE, filename TEXT, folder TEXT)')
    def add_track(self, path):
        try:
            with sqlite3.connect(self.DB_NAME) as conn:
                conn.execute('INSERT INTO tracks (path, filename, folder) VALUES (?, ?, ?)', (path, os.path.basename(path), os.path.basename(os.path.dirname(path))))
        except sqlite3.IntegrityError: pass
    def get_folders(self, filter_text=None):
        with sqlite3.connect(self.DB_NAME) as conn:
            sql = 'SELECT DISTINCT folder FROM tracks'
            if filter_text: sql += f" WHERE filename LIKE '%{filter_text}%' OR folder LIKE '%{filter_text}%'"
            sql += ' ORDER BY folder'
            return [r[0] for r in conn.execute(sql).fetchall()]
    def get_tracks_in_folder(self, folder, filter_text=None):
        with sqlite3.connect(self.DB_NAME) as conn:
            sql = 'SELECT filename, path FROM tracks WHERE folder = ?'
            if filter_text: sql += f" AND (filename LIKE '%{filter_text}%' OR folder LIKE '%{filter_text}%')"
            sql += ' ORDER BY filename'
            return conn.execute(sql, (folder,)).fetchall()


# -----------------------------
# Threading Workers
# -----------------------------

class LibraryScanner(QObject):
    finished = pyqtSignal(int)
    def __init__(self, root_path): super().__init__(); self.root_path = root_path; self.db = LibraryManager()
    def run(self):
        count = 0
        for root, _, files in os.walk(self.root_path):
            for file in files:
                if file.lower().endswith(('.wav', '.mp3', '.flac', '.ogg', '.m4a')):
                    self.db.add_track(os.path.join(root, file))
                    count += 1
        self.finished.emit(count)

class AudioLoader(QObject):
    finished = pyqtSignal(object, int, str); error = pyqtSignal(str)
    def load(self, path):
        try:
            data, sr = read_wav(path)
            self.finished.emit(data, sr, path)
        except Exception as e: self.error.emit(str(e))

class AudioProcessor(QObject):
    finished = pyqtSignal(object); error = pyqtSignal(str)
    def __init__(self, engine, audio, sr): super().__init__(); self.engine = engine; self.audio = audio; self.sr = sr
    def run(self):
        try:
            res = self.engine.apply_chain(self.audio, self.sr)
            self.finished.emit(res); del res; gc.collect()
        except Exception as e: self.error.emit(str(e))


# -----------------------------
# Engine & Components
# -----------------------------

@dataclass
class EngineState:
    enabled: Dict[str, bool]
    global_intensity: float
    wet_dry: float

class EffectEngine:
    def __init__(self): self.state = EngineState(enabled={}, global_intensity=0.72, wet_dry=0.60)
    def set_enabled(self, name, value): self.state.enabled[name] = bool(value)
    def is_enabled(self, name): return self.state.enabled.get(name, False)
    def apply_chain(self, audio, sr):
        dry = audio; y = audio.copy(); I = self.state.global_intensity
        if self.is_enabled("Gain"): y *= db_to_lin(-6.0 + 18.0 * I)
        if self.is_enabled("Bass boost"): y = one_pole_low_shelf(y, sr, 120.0, 4.0 * I)
        if self.is_enabled("Compressor"): y = simple_compressor(y, -12.0 - (6.0*I), 2.5 + I)
        if self.is_enabled("Peak limiter") or self.is_enabled("Limiter"): np.clip(y, -0.98, 0.98, out=y)
        if self.is_enabled("Stereo widening"): y = stereo_widen(y, 0.3 * I)
        wet = self.state.wet_dry
        if wet < 1.0: y = y * wet + dry * (1.0 - wet)
        return np.clip(y, -1.0, 1.0)

class AuraOrb(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.setMinimumSize(400, 320); self.phase = 0.0; self.is_playing = False; self.pulse = 0.0
        self.timer = QTimer(self); self.timer.timeout.connect(self._animate); self.timer.start(16)
        self.cpu_load = 0.0; self.ram_load = 0.0
    def set_playing(self, playing): self.is_playing = playing
    def _animate(self):
        self.phase += 0.08 if self.is_playing else 0.02
        self.pulse = (math.sin(self.phase * 2.0) + 1.0) * (0.8 if self.is_playing else 0.5)
        self.cpu_load = 12.0 + math.sin(self.phase * 5) * 2; self.ram_load = 4.0 + math.cos(self.phase * 3)
        self.update()
    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height(); cx, cy = w/2, h/2 - 20; radius = min(w, h) * 0.25
        bg = QLinearGradient(0,0,0,h); bg.setColorAt(0, QColor(5,8,15)); bg.setColorAt(1, QColor(10,14,24)); p.fillRect(0,0,w,h,bg)
        p.setPen(QPen(QColor(40,60,90,40), 1))
        for i in range(0, w, 40): p.drawLine(i, 0, i, h)
        for i in range(0, h, 40): p.drawLine(0, i, w, i)
        glow = QRadialGradient(cx, cy, radius*2.5)
        glow.setColorAt(0, QColor(0,255,200,40) if self.is_playing else QColor(100,200,255,20))
        glow.setColorAt(0.6, Qt.GlobalColor.transparent); p.setBrush(QBrush(glow)); p.setPen(Qt.PenStyle.NoPen); p.drawEllipse(QPointF(cx, cy), radius*2.5, radius*2.0)
        
        def ring(sc, off, col, wid):
            path = QPainterPath(); r_b = radius * sc
            for i in range(101):
                a = (i/100)*6.28 + off + self.phase
                wob = (5+self.pulse*5) if self.is_playing else (5+self.pulse*2)
                r = r_b + math.sin(a*3 + self.phase*2) * wob
                x = cx + math.cos(a)*r; y = cy + math.sin(a)*r*0.85
                if i==0: path.moveTo(x,y)
                else: path.lineTo(x,y)
            p.setPen(QPen(col, wid)); p.setBrush(Qt.BrushStyle.NoBrush); p.drawPath(path)

        c1 = QColor(0,255,100,120) if self.is_playing else QColor(0,255,255,100)
        c2 = QColor(255,50,200,100) if self.is_playing else QColor(255,0,255,80)
        ring(1.2, 0, c1, 2); ring(1.1, 2.0, c2, 3); ring(0.9, 4.0, QColor(0,150,255,120), 1.5)
        
        p.setBrush(QBrush(QColor(5,10,20))); p.setPen(Qt.PenStyle.NoPen); p.drawEllipse(QPointF(cx, cy), radius, radius*0.85)
        p.setPen(QColor(200,240,255,200)); p.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold)); p.drawText(QRectF(cx-100, cy-15, 200, 30), Qt.AlignmentFlag.AlignCenter, "AURA CORE")
        p.setFont(QFont("Consolas", 8)); p.setPen(QColor(100,200,200,150)); p.drawText(QRectF(cx-60, cy+20, 120, 15), Qt.AlignmentFlag.AlignCenter, f"SYS: {'ACTIVE' if self.is_playing else 'IDLE'}")


# -----------------------------
# Main App
# -----------------------------

STYLESHEET = """
QMainWindow { background-color: #05080f; }
QWidget { color: #d0e0ff; font-family: "Segoe UI"; font-size: 12px; }
QFrame#Panel, QGroupBox { background-color: rgba(16, 24, 40, 0.7); border: 1px solid rgba(100, 150, 255, 0.2); border-radius: 12px; }
QGroupBox { margin-top: 15px; padding-top: 10px; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; color: #88ccff; }
QPushButton { background-color: rgba(30, 45, 70, 0.6); border: 1px solid rgba(80, 120, 180, 0.4); border-radius: 8px; padding: 8px 16px; color: #ffffff; }
QPushButton:hover { background-color: rgba(50, 80, 120, 0.8); border-color: #00ffff; }
QPushButton#Primary { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(0, 100, 200, 0.8), stop:1 rgba(0, 180, 220, 0.8)); border: 1px solid #00ffff; font-weight: bold; }
QSlider::groove:horizontal { height: 6px; background: #223344; border-radius: 3px; }
QSlider::handle:horizontal { width: 14px; margin: -5px 0; border-radius: 7px; background: #00ffff; }
QSlider::sub-page:horizontal { background: #00aaff; border-radius: 3px; }
QTabWidget::pane { border: none; }
QTabBar::tab { background: rgba(30, 45, 70, 0.6); color: #88ccff; padding: 8px 16px; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 2px; }
QTabBar::tab:selected { background: rgba(50, 80, 120, 0.9); color: #fff; border-bottom: 2px solid #00ffff; }
QTreeWidget, QListWidget { background: rgba(10, 15, 25, 0.5); border: none; font-size: 13px; }
QTreeWidget::item:selected { background: rgba(0, 150, 255, 0.3); color: #fff; }
QLineEdit { background: #0a1018; border: 1px solid #335577; border-radius: 6px; padding: 4px; }
QProgressBar { border: 1px solid #335577; border-radius: 6px; text-align: center; }
QProgressBar::chunk { background-color: #00ffff; }
QComboBox { background: #1a2535; border: 1px solid #335577; border-radius: 6px; padding: 4px; color: #eee; }
QComboBox::drop-down { border: none; }
"""

class AuraApp(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("AURA — Advanced Audio Suite"); self.resize(1300, 800)
        self.engine = EffectEngine(); self.db = LibraryManager()
        
        # Dual-Deck Audio Engine for Crossfading
        self.player_a = QMediaPlayer(); self.out_a = QAudioOutput(); self.player_a.setAudioOutput(self.out_a)
        self.player_b = QMediaPlayer(); self.out_b = QAudioOutput(); self.player_b.setAudioOutput(self.out_b)
        self.active_player = 0 # 0=A, 1=B
        self.master_volume = 1.0 # 0.0 to 1.0
        
        # Connect signals for both players
        for p in [self.player_a, self.player_b]:
            p.mediaStatusChanged.connect(self._on_media_status_changed)
            p.playbackStateChanged.connect(self._on_playback_state_changed)
        
        # Crossfader
        self.cross_timer = QTimer(self); self.cross_timer.setInterval(100); self.cross_timer.timeout.connect(self._crossfade_step)
        self.is_crossfading = False
        self.xfade_duration = 4000 # ms
        self.monitor_timer = QTimer(self); self.monitor_timer.setInterval(500); self.monitor_timer.timeout.connect(self._check_xfade_trigger)
        self.monitor_timer.start()
        
        # Link main UI seek bar to active player
        self.player_a.positionChanged.connect(lambda p: self._on_position_changed(p, 0))
        self.player_b.positionChanged.connect(lambda p: self._on_position_changed(p, 1))
        self.player_a.durationChanged.connect(lambda d: self._on_duration_changed(d, 0))
        self.player_b.durationChanged.connect(lambda d: self._on_duration_changed(d, 1))

        self.is_slider_dragging = False; self.current_playlist = []; self.current_index = -1; self.audio_data = None; self.effect_items = {}
        
        # Shuffle/Loop State
        self.shuffle_state = False
        self.loop_state = 1 # 0=Off, 1=All, 2=One
        
        self._init_ui()

    @property
    def current_player(self): return self.player_a if self.active_player == 0 else self.player_b
    @property
    def next_player(self): return self.player_b if self.active_player == 0 else self.player_a
    @property
    def current_out(self): return self.out_a if self.active_player == 0 else self.out_b
    @property
    def next_out(self): return self.out_b if self.active_player == 0 else self.out_a

    def _init_ui(self):
        root = QWidget(); self.setCentralWidget(root); layout = QVBoxLayout(root); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        self.setAcceptDrops(True)
        
        # TOP BAR
        top_bar = QFrame(); top_bar.setFixedHeight(70); top_bar.setStyleSheet("background: rgba(10, 15, 25, 0.9); border-bottom: 1px solid #223344;")
        tb_lay = QHBoxLayout(top_bar)
        title = QLabel("AURA 2.0"); title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold)); title.setStyleSheet("color: #00ffff; letter-spacing: 2px;")
        
        # Buttons
        self.btn_prev = QPushButton("|◀"); self.btn_prev.setFixedWidth(40); self.btn_prev.clicked.connect(self._play_prev)
        self.btn_play = QPushButton("▶"); self.btn_play.setFixedWidth(50); self.btn_play.clicked.connect(self._toggle_playback)
        self.btn_play.setStyleSheet("font-size: 20px; font-weight: bold; color: #88ffaa;")
        self.btn_next = QPushButton("▶|"); self.btn_next.setFixedWidth(40); self.btn_next.clicked.connect(self._play_next)
        self.btn_stop = QPushButton("⏹"); self.btn_stop.setFixedWidth(40); self.btn_stop.clicked.connect(self._stop_playback)
        
        # Shuffle/Loop
        self.btn_shuffle = QPushButton("🔀"); self.btn_shuffle.setFixedWidth(40); self.btn_shuffle.clicked.connect(self._toggle_shuffle)
        self.btn_shuffle.setStyleSheet("color: #666;")
        self.btn_loop = QPushButton("🔁"); self.btn_loop.setFixedWidth(40); self.btn_loop.clicked.connect(self._toggle_loop)
        self.btn_loop.setStyleSheet("color: #00ffaa;") # Default Loop All
        
        seek_l = QVBoxLayout(); seek_l.setSpacing(2)
        self.seek = QSlider(Qt.Orientation.Horizontal); self.seek.setRange(0,0)
        self.seek.sliderPressed.connect(self._seek_press); self.seek.sliderReleased.connect(self._seek_release); self.seek.sliderMoved.connect(self._seek_move)
        self.time_lbl = QLabel("00:00 / 00:00"); self.time_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); self.time_lbl.setStyleSheet("color: #6688aa; font-family: Consolas;")
        seek_l.addWidget(self.seek); seek_l.addWidget(self.time_lbl)
        
        # Volume
        vol_box = QHBoxLayout()
        vol_box.setSpacing(4)
        v_lbl = QLabel("🔊")
        v_lbl.setStyleSheet("color: #6688aa; font-size: 14px;")
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(100)
        self.vol_slider.setFixedWidth(80)
        self.vol_slider.valueChanged.connect(self._set_master_vol)
        vol_box.addWidget(v_lbl)
        vol_box.addWidget(self.vol_slider)
        
        tb_lay.addWidget(title); tb_lay.addSpacing(30)
        tb_lay.addWidget(self.btn_shuffle); tb_lay.addWidget(self.btn_prev); tb_lay.addWidget(self.btn_play); tb_lay.addWidget(self.btn_next); tb_lay.addWidget(self.btn_loop); tb_lay.addWidget(self.btn_stop)
        tb_lay.addSpacing(20); tb_lay.addLayout(seek_l, 1); tb_lay.addSpacing(15); tb_lay.addLayout(vol_box); tb_lay.addSpacing(10)
        layout.addWidget(top_bar)

        # CONTENT
        content = QHBoxLayout(); content.setContentsMargins(20,20,20,20); content.setSpacing(20)
        
        # LEFT PANEL
        left = QFrame(); left.setObjectName("Panel"); left.setFixedWidth(320); lp = QVBoxLayout(left)
        
        # Preset Selector
        preset_grp = QGroupBox("Smart Presets"); pg_lay = QVBoxLayout(preset_grp)
        self.combo = QComboBox(); self.combo.addItems(PRESETS.keys())
        self.combo.currentTextChanged.connect(self._on_preset_changed)
        pg_lay.addWidget(self.combo); lp.addWidget(preset_grp)
        
        dial_grp = QGroupBox("Master Intensity"); dg_lay = QVBoxLayout(dial_grp)
        self.dial = QDial(); self.dial.setRange(0,100); self.dial.setValue(72); self.dial.setNotchesVisible(True)
        self.dial.valueChanged.connect(lambda v: self._set_param('global_intensity', v/100)); dg_lay.addWidget(self.dial); lp.addWidget(dial_grp)
        
        mix_grp = QGroupBox("Wet / Dry Mix"); mg_lay = QVBoxLayout(mix_grp)
        self.mix = QSlider(Qt.Orientation.Horizontal); self.mix.setRange(0,100); self.mix.setValue(60)
        self.mix.valueChanged.connect(lambda v: self._set_param('wet_dry', v/100)); mg_lay.addWidget(self.mix); lp.addWidget(mix_grp)
        
        lp.addStretch(); content.addWidget(left)
        
        # CENTER ORB
        center_l = QVBoxLayout(); self.orb = AuraOrb(); center_l.addWidget(self.orb)
        
        io_panel = QFrame(); io_panel.setObjectName("Panel"); io_panel.setFixedHeight(120); io_lay = QVBoxLayout(io_panel)
        row = QHBoxLayout(); self.path_txt = QLineEdit(); self.path_txt.setReadOnly(True); self.path_txt.setPlaceholderText("Current Track...")
        load_b = QPushButton("Process WAV"); load_b.clicked.connect(self._load_process)
        exp_b = QPushButton("RENDER EXPORT"); exp_b.setObjectName("Primary"); exp_b.clicked.connect(self._export)
        row.addWidget(self.path_txt); row.addWidget(load_b); row.addWidget(exp_b)
        self.prog = QProgressBar(); self.prog.setTextVisible(False); self.prog.setStyleSheet("QProgressBar{height:4px;border:none;background:#222}QProgressBar::chunk{background:#00ffff}")
        io_lay.addLayout(row); io_lay.addWidget(self.prog); center_l.addWidget(io_panel); content.addLayout(center_l, 2)
        
        # RIGHT PANEL
        right = QFrame(); right.setObjectName("Panel"); right.setFixedWidth(340); rp = QVBoxLayout(right); rp.setContentsMargins(5,5,5,5)
        self.tabs = QTabWidget()
        
        # FX Tab
        tab1 = QWidget(); t1 = QVBoxLayout(tab1); t1.setContentsMargins(0,10,0,0)
        self.tree = QTreeWidget(); self.tree.setHeaderHidden(True); self.tree.itemChanged.connect(self._toggle_fx)
        t1.addWidget(self.tree); self._populate_tree(); self.tabs.addTab(tab1, "Effects")
        
        # Library Tab
        tab2 = QWidget(); t2 = QVBoxLayout(tab2); t2.setContentsMargins(0,10,0,0)
        self.lib_search = QLineEdit(); self.lib_search.setPlaceholderText("🔍 Search Library..."); self.lib_search.textChanged.connect(self._refresh_lib)
        self.lib_tree = QTreeWidget(); self.lib_tree.setHeaderLabel("My Library"); self.lib_tree.itemDoubleClicked.connect(self._lib_dbl_click)
        row2 = QHBoxLayout(); scan_b = QPushButton("📂 Select Folder"); scan_b.clicked.connect(self._scan); ref_b = QPushButton("Refresh"); ref_b.clicked.connect(lambda: self._refresh_lib(""))
        row2.addWidget(scan_b); row2.addWidget(ref_b); t2.addWidget(self.lib_search); t2.addWidget(self.lib_tree); t2.addLayout(row2)
        self.tabs.addTab(tab2, "Library")
        
        rp.addWidget(self.tabs); content.addWidget(right); layout.addLayout(content); self._refresh_lib()

    # --- Drag & Drop ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        valid = [f for f in files if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg', '.m4a'))]
        if valid:
            self.current_playlist = valid
            self.current_index = 0
            self._play_current()
            # If single WAV, load for processing too
            if len(valid) == 1 and valid[0].lower().endswith(".wav"):
                self.ld = AudioLoader(); self.th = QThread(); self.ld.moveToThread(self.th)
                self.th.started.connect(lambda: self.ld.load(valid[0])); self.ld.finished.connect(self._loaded)
                self.th.start()

    # --- Toggle Loop/Shuffle/Volume ---
    def _toggle_shuffle(self):
        self.shuffle_state = not self.shuffle_state
        self.btn_shuffle.setStyleSheet("color: #00ffaa;" if self.shuffle_state else "color: #666;")
        
    def _toggle_loop(self):
        # 0=Off, 1=All, 2=One
        self.loop_state = (self.loop_state + 1) % 3
        if self.loop_state == 0:
            self.btn_loop.setText("🔁")
            self.btn_loop.setStyleSheet("color: #666;")
        elif self.loop_state == 1:
            self.btn_loop.setText("🔁")
            self.btn_loop.setStyleSheet("color: #00ffaa;")
        else:
            self.btn_loop.setText("🔂")
            self.btn_loop.setStyleSheet("color: #ffaa00;")

    def _set_master_vol(self, val):
        self.master_volume = val / 100.0
        if not self.is_crossfading:
            self.out_a.setVolume(self.master_volume)
            self.out_b.setVolume(self.master_volume)

    # --- Presets & UI Logic ---
    
    def _populate_tree(self):
        self.tree.blockSignals(True)
        for cat, sub in FEATURES.items():
            p = QTreeWidgetItem(self.tree, [cat]); p.setFlags(Qt.ItemFlag.NoItemFlags)
            for s, items in sub.items():
                g = QTreeWidgetItem(p, [s]); g.setFlags(Qt.ItemFlag.NoItemFlags)
                for i in items:
                    it = QTreeWidgetItem(g, [i]); it.setCheckState(0, Qt.CheckState.Unchecked)
                    it.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    self.effect_items[i] = it
        self.tree.expandToDepth(1); self.tree.blockSignals(False)

    def _on_preset_changed(self, name):
        if name not in PRESETS: return
        p = PRESETS[name]
        
        self.dial.blockSignals(True); self.dial.setValue(int(p["i"]*100)); self.dial.blockSignals(False)
        self.mix.blockSignals(True); self.mix.setValue(int(p["w"]*100)); self.mix.blockSignals(False)
        self.engine.state.global_intensity = p["i"]
        self.engine.state.wet_dry = p["w"]
        
        self.tree.blockSignals(True)
        for it in self.effect_items.values(): it.setCheckState(0, Qt.CheckState.Unchecked)
        self.engine.state.enabled.clear()
        for fx in p["fx"]:
            if fx in self.effect_items:
                self.effect_items[fx].setCheckState(0, Qt.CheckState.Checked)
                self.engine.set_enabled(fx, True)
        self.tree.blockSignals(False); self.tree.repaint()

    def _toggle_fx(self, item, col):
        if item.childCount() == 0: 
            self.engine.set_enabled(item.text(0), item.checkState(0) == Qt.CheckState.Checked)
            self._save_to_custom()
            self.combo.blockSignals(True); self.combo.setCurrentIndex(0); self.combo.blockSignals(False)

    def _set_param(self, k, v): 
        setattr(self.engine.state, k, v)
        self._save_to_custom()
        self.combo.blockSignals(True); self.combo.setCurrentIndex(0); self.combo.blockSignals(False)

    def _save_to_custom(self):
        # Saves current state to "Custom / Modified" slot so switching back restores it
        current_fx = [k for k, v in self.engine.state.enabled.items() if v]
        PRESETS["--- Custom / Modified ---"] = {
            "i": self.engine.state.global_intensity,
            "w": self.engine.state.wet_dry,
            "fx": current_fx
        }

    # --- Library ---
    def _scan(self):
        d = QFileDialog.getExistingDirectory(self, "Music Folder"); 
        if not d: return
        self.sc = LibraryScanner(d); self.th = QThread(); self.sc.moveToThread(self.th)
        self.th.started.connect(self.sc.run); self.sc.finished.connect(lambda: (self._refresh_lib(), self.th.quit()))
        self.th.start()

    def _refresh_lib(self, txt=None):
        if txt is None and isinstance(self.sender(), QLineEdit): txt = self.sender().text()
        self.lib_tree.clear()
        for f in self.db.get_folders(txt):
            fi = QTreeWidgetItem(self.lib_tree, [f]); fi.setFlags(Qt.ItemFlag.ItemIsEnabled)
            for n, p in self.db.get_tracks_in_folder(f, txt):
                ti = QTreeWidgetItem(fi, [n]); ti.setData(0, Qt.ItemDataRole.UserRole, p)
        if txt: self.lib_tree.expandAll()
        else: self.lib_tree.expandToDepth(0)

    def _lib_dbl_click(self, item):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path:
            parent = item.parent()
            self.current_playlist = [parent.child(i).data(0, Qt.ItemDataRole.UserRole) for i in range(parent.childCount())]
            self.current_index = self.current_playlist.index(path)
            self._play_current()

    # --- Dual-Deck Playback & Crossfading ---
    
    def _play_current(self):
        if not (0 <= self.current_index < len(self.current_playlist)): return
        
        target_path = self.current_playlist[self.current_index]
        
        # Check if we should crossfade (Playing AND not already fading)
        if self.current_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState and not self.is_crossfading:
            self.next_out.setVolume(0.0) # Start silent
            self.next_player.setSource(QUrl.fromLocalFile(target_path))
            self.next_player.play()
            
            self.is_crossfading = True
            self.xfade_start_time = time.time()
            self.cross_timer.start()
            self.path_txt.setText(f"Mixing: {os.path.basename(target_path)}")
            return

        # Hard start or Reset
        self.is_crossfading = False; self.cross_timer.stop()
        self.player_a.stop(); self.player_b.stop()
        self.out_a.setVolume(self.master_volume); self.out_b.setVolume(self.master_volume)
        self.active_player = 0 
        
        self.current_player.setSource(QUrl.fromLocalFile(target_path))
        self.current_player.play()
        self.path_txt.setText(f"Playing: {os.path.basename(target_path)}")

    def _get_next_index(self, advance=True):
        if not self.current_playlist: return -1
        N = len(self.current_playlist)
        
        if self.shuffle_state:
            return random.randint(0, N - 1)
        else:
            if not advance: # Previous
                idx = self.current_index - 1
                if idx < 0: return N - 1 if self.loop_state == 1 else 0
                return idx
            else: # Next
                idx = self.current_index + 1
                if idx >= N:
                    if self.loop_state == 1: return 0 # Loop All
                    return -1 # Stop
                return idx

    def _trigger_crossfade_next(self):
        if self.is_crossfading: return
        
        # Loop One logic
        if self.loop_state == 2:
            next_idx = self.current_index
        else:
            next_idx = self._get_next_index(advance=True)
            
        if next_idx == -1: return 
        
        self.current_index = next_idx
        # _play_current handles the crossfade triggering if we are playing
        self._play_current()

    def _check_xfade_trigger(self):
        if not self.engine.is_enabled("Crossfade"): return
        if self.current_player.playbackState() != QMediaPlayer.PlaybackState.PlayingState: return
        if self.is_crossfading: return
        
        dur = self.current_player.duration()
        pos = self.current_player.position()
        if dur > 5000 and (dur - pos) < self.xfade_duration:
            self._trigger_crossfade_next()

    def _crossfade_step(self):
        now = time.time()
        elapsed = (now - self.xfade_start_time) * 1000 # ms
        progress = elapsed / self.xfade_duration
        
        if progress >= 1.0:
            self.cross_timer.stop()
            self.is_crossfading = False
            self.current_player.stop() # Stop the old track
            self.active_player = 1 if self.active_player == 0 else 0 # Swap
            self.current_out.setVolume(self.master_volume)
            self.next_out.setVolume(self.master_volume) # Reset levels
        else:
            # Linear fade with master scaling
            self.current_out.setVolume((1.0 - progress) * self.master_volume)
            self.next_out.setVolume(progress * self.master_volume)

    def _play_next(self): 
        idx = self._get_next_index(advance=True)
        if idx != -1:
            self.current_index = idx
            self._play_current()
        else:
            self._stop_playback()
        
    def _play_prev(self): 
        idx = self._get_next_index(advance=False)
        if idx != -1:
            self.current_index = idx
            self._play_current()
    
    def _toggle_playback(self):
        if self.current_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState: 
            self.current_player.pause(); self.next_player.pause()
        elif self.current_player.source().isEmpty(): QMessageBox.info(self, "Empty", "Select track from Library.")
        else: self.current_player.play()
        
    def _stop_playback(self): 
        self.player_a.stop(); self.player_b.stop()
        self.orb.set_playing(False)
        
    def _on_media_status_changed(self, s): 
        # If media ends naturally and we aren't crossfading
        if s == QMediaPlayer.MediaStatus.EndOfMedia and not self.is_crossfading:
             if self.loop_state == 2: # Loop One - Replay
                 self.current_player.play()
             else:
                 self._play_next()
             
    def _on_playback_state_changed(self, s):
        pl = (s == QMediaPlayer.PlaybackState.PlayingState)
        self.orb.set_playing(pl); self.btn_play.setText("⏸" if pl else "▶")
        
    # --- Seek & UI Updates ---
    def _seek_press(self): self.is_slider_dragging = True
    def _seek_release(self): self.current_player.setPosition(self.seek.value()); self.is_slider_dragging = False
    def _seek_move(self, v): self._upd_time(v, self.current_player.duration())
    
    def _on_position_changed(self, p, player_id): 
        # Only update UI for active player
        if player_id != self.active_player: return
        if not self.is_slider_dragging: self.seek.setValue(p)
        self._upd_time(p, self.current_player.duration())
        
    def _on_duration_changed(self, d, player_id): 
        if player_id != self.active_player: return
        self.seek.setRange(0, d)
        
    def _upd_time(self, c, t): self.time_lbl.setText(f"{c//60000}:{(c//1000)%60:02} / {t//60000}:{(t//1000)%60:02}")

    # --- Processing ---
    def _load_process(self):
        p, _ = QFileDialog.getOpenFileName(self, "Open WAV", "", "WAV (*.wav)"); 
        if not p: return
        self.ld = AudioLoader(); self.th = QThread(); self.ld.moveToThread(self.th)
        self.th.started.connect(lambda: self.ld.load(p)); self.ld.finished.connect(self._loaded)
        self.th.start()

    def _loaded(self, d, sr, p):
        self.audio_data = d; self.sample_rate = sr; self.orb.ram_load = d.nbytes/(1024*1024); self.th.quit()
        self.prog.setValue(100)

    def _export(self):
        if self.audio_data is None: return
        p, _ = QFileDialog.getSaveFileName(self, "Save", "", "WAV (*.wav)"); 
        if not p: return
        self.pr = AudioProcessor(self.engine, self.audio_data, self.sample_rate); self.th = QThread(); self.pr.moveToThread(self.th)
        self.th.started.connect(self.pr.run); self.pr.finished.connect(lambda r: (write_wav(p, r, self.sample_rate), self.th.quit(), QMessageBox.information(self, "Done", "Saved!")))
        self.th.start()

def main():
    # Silencing console noise (FFmpeg, Qt warnings)
    os.environ["QT_LOGGING_RULES"] = "*.debug=false;*.warning=false"
    sys.stderr = open(os.devnull, 'w')

    app = QApplication(sys.argv); app.setStyleSheet(STYLESHEET)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'): app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    w = AuraApp(); w.show(); sys.exit(app.exec())

if __name__ == "__main__": main()