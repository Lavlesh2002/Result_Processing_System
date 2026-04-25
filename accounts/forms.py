from django import forms
from .models import User

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔥 Remove admin option
        self.fields['role'].choices = [
            ('teacher', 'Teacher'),
            ('data_entry', 'Data Entry'),
        ]

    def save(self, commit=True):
        user = super().save(commit=False)

        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)

        if commit:
            user.save()
        return user