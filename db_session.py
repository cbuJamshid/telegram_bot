from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker


url_object = URL.create(
    "postgresql+psycopg2",
    username="olicqunzvtebyx",
    password="4254360e81b06ef068c7a07eda57e463ba621e87afe66f45f26de0a500ed2a29",  # plain (unescaped) text
    host="ec2-34-251-233-253.eu-west-1.compute.amazonaws.com",
    database="d4pmr6b9sqg93s",
    port=5432
)


engine = create_engine(url=url_object, echo=True)

# Create a sessionmaker
Session = sessionmaker(bind=engine)
