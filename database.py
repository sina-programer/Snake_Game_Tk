import peewee as pw
import os


database_name = 'database.db'
database_path = os.path.expanduser(rf'~\.SnakeTk\{database_name}')

db = pw.SqliteDatabase(database_path)
db.connect()


class User(pw.Model):
    username = pw.CharField(unique=True)
    password = pw.CharField()
    is_default = pw.BooleanField(default=False)

    class Meta:
        database = db


class Score(pw.Model):
    user = pw.ForeignKeyField(User)
    score = pw.IntegerField()
    level = pw.IntegerField()
    datetime = pw.DateTimeField()

    class Meta:
        database = db


class Config(pw.Model):
    user = pw.ForeignKeyField(User, backref='configs')
    label = pw.CharField()
    value = pw.CharField()

    @classmethod
    def fetch(cls, user, label):
        try:
            return cls.get(user=user, label=label).value
        except Exception:
            return None

    class Meta:
        database = db


TABLES = [User, Score, Config]

for table in TABLES:  # Create tables
    not db.table_exists(table.__name__) and db.create_tables([table])
