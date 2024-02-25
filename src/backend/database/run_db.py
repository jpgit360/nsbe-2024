from peewee import SqliteDatabase, Model, CharField, IntegerField
from create_db import *

# Query data
# Get all persons
all_persons = Person.select()

# Iterate over the results
for person in all_persons:
    print(person.pid, person.age)

print("------------------------")

all_students = Student.select()

# Iterate over the results
for student in all_students:
    print(student.pid, student.income)


""" all = A.select()

for niga in all:
    print(niga.a, niga.b) """