from django.db import models
from accounts.models import User

class Class(models.Model):
    CLASS_CHOICES = [(str(i), str(i)) for i in range(1, 9)]  # 1–8

    name = models.CharField(max_length=2, choices=CLASS_CHOICES, unique=True)

    def __str__(self):
        return f"Class {self.name}"


class Section(models.Model):
    SECTION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    ]

    name = models.CharField(max_length=1, choices=SECTION_CHOICES)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='sections')

    class Meta:
        unique_together = ('name', 'class_name')

    def __str__(self):
        return f"Class {self.class_name.name} - {self.name}"
    
SUBJECT_CHOICES = [
    ('L1', 'Language 1'),
    ('L2', 'Language 2'),
    ('L3', 'Language 3'),
    ('SCI', 'Science'),
    ('MATH', 'Mathematics'),
    ('SOC', 'Social Science'),
]


class Subject(models.Model):
    name = models.CharField(max_length=10, choices=SUBJECT_CHOICES, unique=True)

    def __str__(self):
        return dict(SUBJECT_CHOICES).get(self.name)    

class TeacherSubject(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.OneToOneField(Subject, on_delete=models.CASCADE)  # 🔥 CHANGE

    def __str__(self):
        return f"{self.teacher.username} - {self.subject}"   