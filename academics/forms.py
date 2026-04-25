from django import forms
from .models import Class, Section
from .models import TeacherSubject, Subject
from accounts.models import User



class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name']
        widgets = {
            'name': forms.Select(attrs={'class': 'form-control'})
        }


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name', 'class_name']
        widgets = {
            'name': forms.Select(attrs={'class': 'form-control'}),
            'class_name': forms.Select(attrs={'class': 'form-control'})
        }

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']
class TeacherSubjectForm(forms.Form):
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(role='teacher')
    )

    subjects = forms.ModelChoiceField(
        queryset=Subject.objects.none()  # initially empty
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔥 exclude already assigned subjects
        assigned_subjects = TeacherSubject.objects.values_list('subject_id', flat=True)

        self.fields['subjects'].queryset = Subject.objects.exclude(id__in=assigned_subjects)