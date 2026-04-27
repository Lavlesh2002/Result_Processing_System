from django.db import models
from student.models import Student
from academics.models import Subject
# Create your models here.



class FraudAlert(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)

    issue = models.CharField(max_length=100)
    risk_level = models.CharField(max_length=20)

    marks = models.IntegerField(null=True, blank=True)
    extra_info = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.issue} ({self.risk_level})"