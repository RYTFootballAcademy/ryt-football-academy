from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///academy_crm.db")
SessionLocal = sessionmaker(bind=engine)

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    position = Column(String)
    parent_id = Column(Integer, ForeignKey("parents.id"))

class Parent(Base):
    __tablename__ = "parents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    contact = Column(String)
    players = relationship("Player", backref="parent")

class Fee(Base):
    __tablename__ = "fees"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    amount = Column(Integer)
    status = Column(String)
    due_date = Column(String)

class Trial(Base):
    __tablename__ = "trials"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    player_id = Column(Integer, ForeignKey("players.id"))
    result = Column(String)

class Tournament(Base):
    __tablename__ = "tournaments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    start_date = Column(String)
    end_date = Column(String)
