from django.db import models
from student.models import Student
from academics.models import Subject
from accounts.models import User
# Create your models here.
class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)

    marks = models.IntegerField()

    # future use
    verified = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'subject')

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.marks}"
