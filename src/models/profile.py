from dataclasses import dataclass
from datetime import datetime
from enum import Enum
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
    password_hash: str
    registration_date: datetime
    status: ProfileStatusEnum
    name: str
    surname: str
    patronymic: str
    stack: str
    skills: str
    experience: str
    desired_role: str
    busyness: str
    contact_mail: str
    contact_number: str
    work_place: str
    work_position: str
    city: str
    portfolio: str
    about: str
