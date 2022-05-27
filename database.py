import peewee as pw


db = pw.SqliteDatabase('database.db')
db.connect()


class User(pw.Model):
    username = pw.CharField(unique=True)
    password = pw.CharField()

    class Meta:
        database = db


class Score(pw.Model):
    user = pw.ForeignKeyField(User)
    score = pw.IntegerField()
    level = pw.IntegerField()
    datetime = pw.DateTimeField()

    class Meta:
        database = db


class Color(pw.Model):
    user = pw.ForeignKeyField(User)
    code = pw.CharField(7)
    type = pw.CharField()

    class Meta:
        database = db


TABLES = [User, Score, Color]

for table in TABLES:  # Create tables
    not db.table_exists(table.__name__) and db.create_tables([table])
