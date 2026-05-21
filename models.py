from sqlalchemy import Column, Integer, String, Text, ForeignKey
from db import base


class User(base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    email = Column(String(100), unique=True)

    password = Column(String(100))


class Report(base):

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    resume_text = Column(Text)

    results = Column(Text)