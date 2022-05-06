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

    class Meta:
        database = db


class Color(pw.Model):
    user = pw.ForeignKeyField(User)
    code = pw.CharField(7)
    type = pw.CharField()

    class Meta:
        database = db


# Create tables
not db.table_exists('User') and db.create_tables([User])
not db.table_exists('Score') and db.create_tables([Score])
not db.table_exists('Color') and db.create_tables([Color])
