
from django.db import models
from academics.models import Class, Section

# Create your models here.


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.roll_number})"