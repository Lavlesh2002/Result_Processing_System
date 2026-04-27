
from django.db import models
from academics.models import Class, Section
import datetime
# Create your models here.


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.roll_number})"
    

def generate_apaar_id():
    year = datetime.datetime.now().year
    last = ApaarProfile.objects.count() + 1
    return f"APAAR{year}{str(last).zfill(4)}"

class ApaarProfile(models.Model):
    student = models.OneToOneField('Student', on_delete=models.CASCADE)
    apaar_id = models.CharField(max_length=20, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.apaar_id:
            self.apaar_id = generate_apaar_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.name} - {self.apaar_id}"
