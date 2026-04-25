from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.forms import UserCreationForm
from accounts.models import User
from academics.models import Class, Section
from academics.forms import ClassForm, SectionForm
from academics.models import Subject, TeacherSubject
from academics.forms import SubjectForm, TeacherSubjectForm
# from students.models import Student   # (you will create this soon)
# from results.models import Result     # (future module)
# ================= DASHBOARD REDIRECT ================= #

@login_required
def dashboard_redirect(request):
    role = getattr(request.user, 'role', None)

    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'teacher':
        return redirect('teacher_dashboard')
    elif role == 'data_entry':
        return redirect('data_entry_dashboard')
    else:
        return redirect('login')


# ================= DASHBOARDS ================= #

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('login')
    return render(request, 'dashboard/admin/home.html')


@login_required
def teacher_dashboard(request):
    if request.user.role != 'teacher':
        return redirect('login')
    return render(request, 'dashboard/teacher/home.html')


@login_required
def data_entry_dashboard(request):
    if request.user.role != 'data_entry':
        return redirect('login')
    return render(request, 'dashboard/data_entry/home.html')


# ================= USER MANAGEMENT ================= #

@login_required
def manage_users(request):
    if request.user.role != 'admin':
        return redirect('login')

    # Show only teacher and data entry users
    users = User.objects.filter(role__in=['teacher', 'data_entry'])

    return render(request, 'dashboard/admin/users.html', {'users': users})


@login_required
def add_user(request):
    if request.user.role != 'admin':
        return redirect('login')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_users')
    else:
        form = UserCreationForm()

    return render(request, 'dashboard/admin/add_user.html', {'form': form})


@login_required
def edit_user(request, user_id):
    if request.user.role != 'admin':
        return redirect('login')

    user = get_object_or_404(User, id=user_id)

    # Prevent editing admin or self
    if user.role == 'admin' or user == request.user:
        return redirect('manage_users')

    if request.method == 'POST':
        form = UserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('manage_users')
    else:
        form = UserCreationForm(instance=user)

    return render(request, 'dashboard/admin/edit_user.html', {'form': form})


@login_required
def toggle_user(request, user_id):
    if request.user.role != 'admin':
        return redirect('login')

    user = get_object_or_404(User, id=user_id)

    # Prevent blocking admin or self
    if user.role == 'admin' or user == request.user:
        return redirect('manage_users')

    user.is_active = not user.is_active
    user.save()

    return redirect('manage_users')


@login_required
def delete_user(request, user_id):
    if request.user.role != 'admin':
        return redirect('login')

    user = get_object_or_404(User, id=user_id)

    # Prevent deleting admin or self
    if user.role == 'admin' or user == request.user:
        return redirect('manage_users')

    user.delete()
    return redirect('manage_users')

@login_required
def manage_academics(request):
    if request.user.role != 'admin':
        return redirect('login')

    classes = Class.objects.all()
    sections = Section.objects.all()

    return render(request, 'dashboard/admin/academics.html', {
        'classes': classes,
        'sections': sections
    })

@login_required
def add_class(request):
    if request.user.role != 'admin':
        return redirect('login')

    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_academics')
    else:
        form = ClassForm()

    return render(request, 'dashboard/admin/add_class.html', {'form': form})
@login_required
def add_section(request):
    if request.user.role != 'admin':
        return redirect('login')

    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_academics')
    else:
        form = SectionForm()

    return render(request, 'dashboard/admin/add_section.html', {'form': form})

@login_required
def delete_class(request, id):
    if request.user.role != 'admin':
        return redirect('login')

    obj = Class.objects.get(id=id)
    obj.delete()

    return redirect('manage_academics')

@login_required
def delete_section(request, id):
    if request.user.role != 'admin':
        return redirect('login')

    obj = Section.objects.get(id=id)
    obj.delete()

    return redirect('manage_academics')



@login_required
def manage_subjects(request):
    if request.user.role != 'admin':
        return redirect('login')

    subjects = Subject.objects.all()
    mappings = TeacherSubject.objects.select_related('teacher', 'subject')

    return render(request, 'dashboard/admin/subjects.html', {
        'subjects': subjects,
        'mappings': mappings
    })

@login_required
def add_subject(request):
    if request.user.role != 'admin':
        return redirect('login')

    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_subjects')
    else:
        form = SubjectForm()

    return render(request, 'dashboard/admin/add_subject.html', {'form': form})

@login_required
def assign_teacher_subject(request):
    if request.user.role != 'admin':
        return redirect('login')

    if request.method == 'POST':
        form = TeacherSubjectForm(request.POST)
        if form.is_valid():
            teacher = form.cleaned_data['teacher']
            subject = form.cleaned_data['subjects']

            # 🔒 safety check
            if not TeacherSubject.objects.filter(subject=subject).exists():
                TeacherSubject.objects.create(
                    teacher=teacher,
                    subject=subject
                )

            return redirect('manage_subjects')
    else:
        form = TeacherSubjectForm()

    return render(request, 'dashboard/admin/assign_subject.html', {'form': form})

@login_required
def delete_mapping(request, id):
    if request.user.role != 'admin':
        return redirect('login')

    obj = TeacherSubject.objects.get(id=id)
    obj.delete()

    return redirect('manage_subjects')

# @login_required
# def admin_dashboard(request):
#     if request.user.role != 'admin':
#         return redirect('login')

#     context = {
#         'users_count': User.objects.count(),
#         'class_count': Class.objects.count(),
#         'subject_count': Subject.objects.count(),
#         'teacher_count': User.objects.filter(role='teacher').count(),

#         # NEW
#         'student_count': Student.objects.count(),
#         'pending_results': Result.objects.filter(verified=False).count(),
#         'completed_results': Result.objects.filter(verified=True).count(),
#     }

#     return render(request, 'dashboard/admin/home.html', context)