from database.models import *


db.bind(provider='sqlite', filename='reviews.db', create_db=True)
db.generate_mapping(create_tables=True)
