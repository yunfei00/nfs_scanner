from __future__ import annotations

import logging
import threading
from queue import Queue, Empty
from typing import Optional

import serial

logger = logging.getLogger(__name__)


class SerialHelper:
    """线程安全的串口封装，负责收发与后台读取线程。"""

    def __init__(self) -> None:
        self._serial: Optional[serial.Serial] = None
        self._lock = threading.Lock()
        self._read_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._rx_queue: "Queue[bytes]" = Queue()

    def open(self, port: str, baudrate: int = 115200, timeout: float = 0.1) -> None:
        with self._lock:
            if self._serial and self._serial.is_open:
                return
            self._serial = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
            self._stop_event.clear()
            self._read_thread = threading.Thread(
                target=self._read_loop, daemon=True
            )
            self._read_thread.start()
            logger.info("Serial opened on %s", port)

    def close(self) -> None:
        with self._lock:
            self._stop_event.set()
            if self._serial and self._serial.is_open:
                self._serial.close()
                logger.info("Serial closed")

    def write_line(self, line: str) -> None:
        with self._lock:
            if not self._serial or not self._serial.is_open:
                raise RuntimeError("Serial not open")
            data = (line.strip() + "\n").encode("ascii")
            self._serial.write(data)
            logger.debug("Serial write: %s", line.strip())

    def read_line(self, timeout: float = 0.1) -> Optional[str]:
        try:
            data = self._rx_queue.get(timeout=timeout)
        except Empty:
            return None
        return data.decode("ascii", errors="ignore").strip()

    def _read_loop(self) -> None:
        if not self._serial:
            return
        while not self._stop_event.is_set():
            try:
                line = self._serial.readline()
                if line:
                    self._rx_queue.put(line)
            except Exception as exc:  # noqa: BLE001
                logger.error("Serial read error: %s", exc)
                break
