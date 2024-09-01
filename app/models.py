from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Port(Base):
    __tablename__ = "ports"

    id = Column(Integer, primary_key=True, index=True)
    port_code = Column(String(5), unique=True, index=True)
    name = Column(String, index=True)
    region_slug = Column(String, index=True)

class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True)
    name = Column(String)
    parent_slug = Column(String, index=True)

class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    origin_port_code = Column(String(5), ForeignKey('ports.port_code'))
    destination_port_code = Column(String(5), ForeignKey('ports.port_code'))
    date = Column(Date, index=True)
    price = Column(Float)
