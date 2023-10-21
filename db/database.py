from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

from config.init_folders import Folders

engine = create_engine(f"sqlite:///{Folders.DB_PATH}/base.db")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
