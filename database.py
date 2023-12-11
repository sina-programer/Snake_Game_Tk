import peewee as pw
import os


db_name = 'database.db'
db_directory = '.SnakeTk'
db_path = os.path.expanduser(rf'~\{db_directory}\{db_name}')
db_parent_dir = os.path.dirname(db_path)

if not os.path.exists(db_parent_dir):
	os.mkdir(db_parent_dir)

db = pw.SqliteDatabase(db_path)
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
