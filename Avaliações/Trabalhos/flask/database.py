import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

# Load environment variables from .env file
load_dotenv()

# Define the database connection URL
db_path = os.getenv("DB_PATH")

if not db_path:
    raise ValueError("DB_PATH environment variable is not set")

engine = create_engine('sqlite:///' + db_path)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")

if __name__ == '__main__':
    init_db()