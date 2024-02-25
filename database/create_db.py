from peewee import *

# Connect to SQLite database
db = SqliteDatabase('example.db')

# Define your models
class BaseModel(Model):
    class Meta:
        database = db

""" class A(BaseModel):
    a = AutoField()
    b = IntegerField() """

class Person(BaseModel):
    pid = AutoField()
    name = CharField()
    age = IntegerField()
    gender = CharField()
    dob = DateField()
    email = CharField()  

class Student(BaseModel):
    pid = ForeignKeyField(Person)
    income = IntegerField()
    location = CharField()
    grade_level = IntegerField()

class Tutor(BaseModel):
    pid = ForeignKeyField(Person)
    subjects = CharField()
    university = CharField()

# Create tables
def create_tables():
    with db:
        #db.create_tables([A])
        db.create_tables([Person])
        db.create_tables([Student])
        db.create_tables([Tutor])

if __name__ == "__main__":
    # Create tables when running the script
    create_tables()


# Connect to database
#db.connect()

