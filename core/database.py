from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    encoding = Column(LargeBinary, nullable=False)
    attendances = relationship("Attendance", back_populates="student")

class Attendance(Base):
    __tablename__ = 'attendance'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    timestamp = Column(DateTime, default=datetime.now)
    student = relationship("Student", back_populates="attendances")

def init_db(url='sqlite:///attendance.db'):
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
