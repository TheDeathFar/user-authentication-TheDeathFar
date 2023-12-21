import datetime
from string import ascii_lowercase, ascii_uppercase, punctuation, digits
from typing import Optional
from pydantic import BaseModel, validator, ValidationError, field_validator
import re

alphabets = ascii_lowercase, ascii_uppercase, punctuation, digits


class UserValidator(BaseModel):
    email: str
    password: str
    intervals: list[list[float]]
    holdings_time: list[list[float]]

    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email format")
        return value

    @field_validator('password')
    @classmethod
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError('The password must consist of at least 6 characters!')
        return value