from sqlalchemy import Column, String, DateTime, Boolean, ARRAY, Index, Integer, Enum, \
    JSON, Interval, BigInteger, Float
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import validates

from models.consts import AnimalsType

try:
    from sqlalchemy.orm import declarative_base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base

from models import utils

BASE = declarative_base(cls=utils.Model)
SCHEMA = 'public'  # Define schema name for all tables

ANIMALS_TYPES_ENUM = Enum(AnimalsType, name='AnimalsTypesEnum', schema=SCHEMA, create_type=True)


class Animal(BASE):
    __tablename__ = 'animals'  # Single table for both Feed and BlazeFeed
    __table_args__ = (
        Index(
            'idx_lineages',
            'name', 'dob', 'type',
        ),
        {'extend_existing': True, 'schema': SCHEMA},
    )

    # id = Column(BigInteger, autoincrement=True, primary_key=True)
    name = Column(String, nullable=False, primary_key=True)
    dob = Column(DateTime, nullable=False, )
    type = Column(ANIMALS_TYPES_ENUM, nullable=False, default=AnimalsType.SHEEP)

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=func.now(), nullable=False)

    @validates('name', )
    def convert_to_upper(self, key, value):
        """Ensure the field is always uppercase."""
        return value.upper()



