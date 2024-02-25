from create_db import *
from datetime import date

# Insert data
person1 = Person(name="bob", age=3, gender="male", dob=date(2022, 1, 15), email="bruh")
person1.save()

student1 = Student(pid = 1, income=2, location='canada', grade_level=4)
student1.save()

""" a_1 = A(b=2)
a_1.save() """