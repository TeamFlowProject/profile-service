from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class ProfileStatusEnum(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"


@dataclass
class Profile:
    """
    Profile dataclass model
    """

    id: uuid.UUID
    mail: str = ""
    password_hash: str = ""
    registration_date: datetime = field(default_factory=datetime.now)
    name: str = ""
    surname: str = ""
    patronymic: str = ""
    stack: str = ""
    skills: str = ""
    experience: str = ""
    desired_role: str = ""
    busyness: str = ""
    contact_mail: str = ""
    contact_number: str = ""
    work_place: str = ""
    work_position: str = ""
    city: str = ""
    portfolio: str = ""
    about: str = ""
    status: Optional[ProfileStatusEnum] = None
