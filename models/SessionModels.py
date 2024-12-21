from sqlalchemy import Column, Integer, String, Text

from model import BaseWithUtils


# pydantic models (can be used for param parsing)

# SQL ORM Models
class UploaderSessionEncrypted(BaseWithUtils):
    __tablename__ = "uploader_sessions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_maker_name = Column(String, default=None)
    encrypted_configuration = Column(Text, default=None)
