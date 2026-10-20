
import os
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

load_dotenv()

url = URL.create(
    "postgresql+psycopg",
    username=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5433")),
    database=os.environ["POSTGRES_DB"],
)

engine = create_engine(url)

try:
    with engine.connect() as connection:
        version = connection.execute(
            text("SELECT version()")
        ).scalar_one()

        print("PostgreSQL connection successful!")
        print(version)
finally:
    engine.dispose()
