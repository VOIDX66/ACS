"""
Sistema de Procesamiento de Vídeos con Prioridades
====================================================
Modelos de datos y enumeraciones.
"""

import time
from dataclasses import dataclass, field
from enum import Enum


class Priority(Enum):
    PREMIUM = 1
    FREE    = 2

    def label(self) -> str:
        return "Premium" if self == Priority.PREMIUM else "Gratuito"


@dataclass
class Job:
    job_id     : str
    video_name : str
    client_name: str
    priority   : Priority
    arrival_time: float = field(default_factory=time.time)
    forced_free : bool  = False          # marcado por la estrategia anti-inanición

    def __str__(self) -> str:
        return f"[{self.video_name}] de {self.client_name} ({self.priority.label()})"