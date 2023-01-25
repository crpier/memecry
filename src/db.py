from src import models

engine = models.get_engine()
models.Base.metadata.create_all(engine)
session = models.get_sessionmaker(engine)()
