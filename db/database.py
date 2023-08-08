from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

import config.db_config

engine = create_engine(f"sqlite:///{config.db_config.DB_PATH}", echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
