import face_recognition

from typing import List
from typing import Any
import numpy as np
from dataclasses import dataclass
import json


@dataclass
class Human:
    identifier_employer: str
    name_employer: str
    lastname_employer: str
    email_employer: str
    id_employer: int
    create_at: str
    is_active: bool
    face_coding_employer: np.ndarray
