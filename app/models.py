from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # One repository has many files
    files = relationship(
        "File",
        back_populates="repository",
        cascade="all, delete"
    )


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    language = Column(String, nullable=True)
    size = Column(Integer, nullable=True)

    repo_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"))

    # Relationship back to Repository
    repository = relationship(
        "Repository",
        back_populates="files"
    )

    # One file has many chunks
    chunks = relationship(
        "CodeChunk",
        back_populates="file",
        cascade="all, delete"
    )


class CodeChunk(Base):
    __tablename__ = "code_chunks"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    class_name = Column(String, nullable=True)
    method_name = Column(String, nullable=True)
    start_line = Column(Integer, nullable=True)
    end_line = Column(Integer, nullable=True)

    file_id = Column(Integer, ForeignKey("files.id", ondelete="CASCADE"))

    # Relationship back to File
    file = relationship(
        "File",
        back_populates="chunks"
    )