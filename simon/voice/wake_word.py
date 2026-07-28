import logging
import math
import queue
import threading
from typing import Callable, Optional

import numpy as np
import pyaudio

LOGGER = logging.getLogger("simon.voice.wake")


class WakeWordDetector:
    def __init__(self, on_trigger: Callable[[], None], chunk: int = 1024, rate: int = 16000, cooldown: float = 1.5) -> None:
        self.on_trigger = on_trigger
        self.chunk = chunk
        self.rate = rate
        self.cooldown = cooldown
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def _rms(self, frame: bytes) -> float:
        try:
            samples = np.frombuffer(frame, dtype=np.int16)
            if samples.size == 0:
                return 0.0
            return math.sqrt(float(np.mean(samples.astype(np.float32) ** 2)))
        except Exception:
            return 0.0

    def _listen(self) -> None:
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
            LOGGER.exception("Cannot open microphone")
            return

        last_trigger = 0.0
        energy_history = []
        window_size = 8

        try:
            while self._running:
                try:
                    frame = stream.read(self.chunk, exception_on_overflow=False)
                except Exception:
                    continue

                energy = self._rms(frame)
                energy_history.append(energy)
                if len(energy_history) > window_size:
                    energy_history.pop(0)

                if len(energy_history) < window_size:
                    continue

                avg_energy = sum(energy_history) / len(energy_history)
                if avg_energy < 400:
                    energy_history.clear()
                    continue

                peaks = sum(1 for e in energy_history if e > avg_energy * 2.2)
                now = __import__("time").time()
                if peaks >= 2 and (now - last_trigger) >= self.cooldown:
                    last_trigger = now
                    energy_history.clear()
                    try:
                        self.on_trigger()
                    except Exception:
                        LOGGER.exception("Wake trigger failed")
        finally:
            try:
                stream.stop_stream()
                stream.close()
            except Exception:
                pass
            pa.terminate()

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None
