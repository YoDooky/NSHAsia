from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
import config.db_config

# Create a SQLite in-memory database
engine = create_engine(f"sqlite:///{config.db_config.DB_PATH}", echo=True)
Base = declarative_base()


class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    # One-to-many relationship with Employee
    employees = relationship('Employee', back_populates='department')


class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    department_id = Column(Integer, ForeignKey('departments.id'))

    # Many-to-one relationship with Department
    department = relationship('Department', back_populates='employees')


# Create the tables in the database
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Add some data to the database
dept1 = Department(name='Engineering')
dept2 = Department(name='HR')

emp1 = Employee(name='Alice', age=30, department=dept1)
emp2 = Employee(name='Bob', age=25, department=dept1)
emp3 = Employee(name='Carol', age=35, department=dept2)

session.add_all([dept1, dept2, emp1, emp2, emp3])
session.commit()

s = session.query(Department).all()
print(s)
