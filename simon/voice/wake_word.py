"""
Simon Wake Word Detector – Energy-based voice activity detection.
Triggers a callback when sustained speech energy is detected.
Improved accuracy with configurable thresholds and frequency analysis.
"""

import logging
import math
import threading
import time
from typing import Callable, Optional

import numpy as np

LOGGER = logging.getLogger("simon.voice.wake")


class WakeWordDetector:
    """
    Detects voice activity via sustained energy peaks from the microphone.
    Calls `on_trigger()` when wake activity is detected.
    """

    def __init__(
        self,
        on_trigger: Callable[[], None],
        chunk: int = 1024,
        rate: int = 16000,
        cooldown: float = 2.0,
        energy_threshold: float = 500,
        peak_ratio: float = 2.2,
        min_peaks: int = 3,
        window_size: int = 10,
    ) -> None:
        self.on_trigger = on_trigger
        self.chunk = chunk
        self.rate = rate
        self.cooldown = cooldown
        self.energy_threshold = energy_threshold
        self.peak_ratio = peak_ratio
        self.min_peaks = min_peaks
        self.window_size = window_size
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._on_status: Optional[Callable[[str], None]] = None

    def set_status_callback(self, callback: Callable[[str], None]) -> None:
        """Set a callback to receive status updates (e.g., for GUI display)."""
        self._on_status = callback

    def _emit_status(self, status: str) -> None:
        if self._on_status:
            try:
                self._on_status(status)
            except Exception:
                pass

    def _rms(self, frame: bytes) -> float:
        """Calculate Root Mean Square energy of audio frame."""
        try:
            samples = np.frombuffer(frame, dtype=np.int16)
            if samples.size == 0:
                return 0.0
            return math.sqrt(float(np.mean(samples.astype(np.float32) ** 2)))
        except Exception:
            return 0.0

    def _has_speech_frequency(self, frame: bytes) -> bool:
        """Basic frequency check: human speech is typically 85-3000 Hz."""
        try:
            samples = np.frombuffer(frame, dtype=np.int16).astype(np.float32)
            if samples.size < self.chunk:
                return False
            fft = np.abs(np.fft.rfft(samples))
            freqs = np.fft.rfftfreq(len(samples), 1.0 / self.rate)

            # Focus on speech frequency range (85-3000 Hz)
            speech_mask = (freqs >= 85) & (freqs <= 3000)
            speech_energy = np.sum(fft[speech_mask])
            total_energy = np.sum(fft)

            if total_energy == 0:
                return False

            # Speech should dominate the frequency spectrum
            return (speech_energy / total_energy) > 0.4
        except Exception:
            return True  # Fallback: assume it's speech

    def _listen(self) -> None:
        """Main listening loop."""
        import pyaudio

        pa = pyaudio.PyAudio()
        try:
            stream = pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
            )
        except Exception as exc:
            LOGGER.exception("Cannot open microphone for wake word")
            self._emit_status("Lỗi microphone")
            return

        last_trigger = 0.0
        energy_history: list[float] = []

        self._emit_status("Đang lắng nghe wake word...")
        LOGGER.info("Wake word detector started (threshold=%.0f, peaks=%d)", self.energy_threshold, self.min_peaks)

        try:
            while self._running:
                try:
                    frame = stream.read(self.chunk, exception_on_overflow=False)
                except Exception:
                    continue

                energy = self._rms(frame)
                energy_history.append(energy)
                if len(energy_history) > self.window_size:
                    energy_history.pop(0)

                if len(energy_history) < self.window_size:
                    continue

                avg_energy = sum(energy_history) / len(energy_history)

                # Below threshold – reset and skip
                if avg_energy < self.energy_threshold:
                    energy_history.clear()
                    continue

                # Check for speech-like peaks
                peaks = sum(1 for e in energy_history if e > avg_energy * self.peak_ratio)
                now = time.time()

                if peaks >= self.min_peaks and (now - last_trigger) >= self.cooldown:
                    # Additional frequency check to reduce false positives
                    if self._has_speech_frequency(frame):
                        last_trigger = now
                        energy_history.clear()
                        self._emit_status("Wake word detected!")
                        LOGGER.info("Wake word triggered (peaks=%d, avg_energy=%.0f)", peaks, avg_energy)
                        try:
                            self.on_trigger()
                        except Exception:
                            LOGGER.exception("Wake trigger callback failed")
                        self._emit_status("Đang lắng nghe wake word...")
        finally:
            try:
                stream.stop_stream()
                stream.close()
            except Exception:
                pass
            pa.terminate()

    def start(self) -> None:
        """Start the wake word detection in a background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._listen, daemon=True, name="simon-wake-word")
        self._thread.start()
        LOGGER.info("Wake word detector started")

    def stop(self) -> None:
        """Stop the wake word detection."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
            self._thread = None
        LOGGER.info("Wake word detector stopped")

    @property
    def is_running(self) -> bool:
        return self._running
