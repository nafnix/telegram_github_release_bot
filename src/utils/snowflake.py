import threading
from datetime import UTC, datetime
from time import sleep, time
from typing import Callable

from src.config import settings


class SnowFlake:
    @staticmethod
    def __current_timestamp():
        return int(time() * 1000)

    def __init__(
        self,
        worker_id_bits: int = 10,
        sequence_bits: int = 12,
        start_timestamp: int = int(
            datetime(2024, 1, 1, tzinfo=UTC).timestamp() * 1e3
        ),
    ) -> None:
        self._worker_id_bits = worker_id_bits
        self._max_worker_id = 2**worker_id_bits - 1

        self._sequence_bits = sequence_bits
        self._max_millisecond_count = 2**sequence_bits - 1

        self._start_timestamp = start_timestamp

        self._last_timestamp = -1
        self._times = 0
        self._lock = threading.Lock()

    @property
    def worker_id_bits(self) -> int:
        return self._worker_id_bits

    @property
    def max_worker_id(self) -> int:
        return self._max_worker_id + 1

    @property
    def sequence_bits(self) -> int:
        return self._sequence_bits

    @property
    def max_millisecond_count(self) -> int:
        return self._max_millisecond_count + 1

    @property
    def start_timestamp(self) -> int:
        return self._start_timestamp

    def __call__(self, worker_id: int) -> Callable[..., int]:
        if self.max_worker_id < worker_id:
            msg = "Exceeds maximum value"
            raise ValueError(msg)

        if worker_id < 1:
            msg = "Below minimum value"
            raise ValueError(msg)

        worker_id -= 1

        def generator():
            with self._lock:
                assert worker_id <= self.max_worker_id

                current_timestamp_ = self.__current_timestamp()

                if current_timestamp_ < self._last_timestamp:
                    sleep(self._last_timestamp - current_timestamp_)
                    self._times = 0

                if current_timestamp_ == self._last_timestamp:
                    self._times = (
                        self._times + 1
                    ) & self._max_millisecond_count
                    if self._times == 0:
                        sleep(0.001)
                        current_timestamp_ = self.__current_timestamp()
                else:
                    self._times = 0

                self._last_timestamp = current_timestamp_

                passed_timestamp = current_timestamp_ - self._start_timestamp

                result = (
                    passed_timestamp
                    << self._worker_id_bits
                    << self._sequence_bits
                )

                result |= worker_id << self._sequence_bits

                result |= self._times

                return result

        return generator


snowflake = SnowFlake(10, 12)
snowflake_worker = snowflake(settings.SNOW_FLAKE_WORKER_ID)
