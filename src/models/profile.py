from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class Profile:
    """
    Temp profile model based on the frontend representation
    Must be harmonized with backend
    """
    id: uuid.UUID
    login: str
    # password_hash: ?
    registration_date: datetime
    full_name: str
    stack: list[str]
    skills: list[str]
    experience: str
    desired_role: str
    busyness: str
    contact_mail: str
    phone: str
    work_place: str
    work_position: str
    city: str
    portfolio: str
    about: str
