# create_tables.py
from backend.database.session import Base, engine
from backend.database.models.page_config import PageConfig

Base.metadata.create_all(bind=engine)
print("Tables created!")
