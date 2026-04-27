from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.forms import UserCreationForm
from accounts.models import User
from academics.models import Class, Section
from academics.forms import ClassForm, SectionForm
from academics.models import Subject, TeacherSubject
from academics.forms import SubjectForm, TeacherSubjectForm
from student.models import Student   
from student.forms import StudentForm
from results.models import Result  
from django.db.models import Sum
from audit.utils import log_action
from student.models import ApaarProfile
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

    # ================= COUNTS ================= #
    users_count = User.objects.filter(is_superuser=False).count()

    class_count = Class.objects.count()
    subject_count = Subject.objects.count()
    teacher_count = User.objects.filter(role='teacher').count()
    student_count = Student.objects.count()

    # ================= RESULTS ================= #
    completed_results = Result.objects.count()

    #  total expected results = students × subjects
    total_expected = student_count * subject_count

    pending_results = total_expected - completed_results

    # ================= CONTEXT ================= #
    context = {
        'users_count': users_count,
        'class_count': class_count,
        'subject_count': subject_count,
        'teacher_count': teacher_count,
        'student_count': student_count,
        'completed_results': completed_results,
        'pending_results': pending_results,
    }

    return render(request, 'dashboard/admin/home.html', context)





@login_required
def teacher_dashboard(request):
    if request.user.role != 'teacher':
        return redirect('login')

    #  TOTAL STUDENTS
    student_count = Student.objects.count()

    #  SUBJECTS ASSIGNED TO TEACHER
    subject_qs = TeacherSubject.objects.filter(teacher=request.user)
    subject_count = subject_qs.count()

    #  GET SUBJECT IDs
    subject_ids = subject_qs.values_list('subject_id', flat=True)

    #  COMPLETED MARKS (ONLY FOR THIS TEACHER'S SUBJECTS)
    completed_marks = Result.objects.filter(
        subject_id__in=subject_ids
    ).count()

    #  TOTAL EXPECTED
    total_expected = student_count * subject_count

    #  PENDING
    pending_marks = total_expected - completed_marks

    context = {
        'student_count': student_count,
        'subject_count': subject_count,
        'completed_marks': completed_marks,
        'pending_marks': pending_marks
    }

    return render(request, 'dashboard/teacher/home.html', context)


@login_required
def data_entry_dashboard(request):
    if request.user.role != 'data_entry':
        return redirect('login')

    #  TOTAL STUDENTS (GLOBAL)
    student_count = Student.objects.count()

    #  OPTIONAL (if you track who added student)
    # student_count = Student.objects.filter(created_by=request.user).count()

    context = {
        'student_count': student_count
    }

    return render(request, 'dashboard/data_entry/home.html', context)


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
def admin_manage_students(request):
    if request.user.role != 'admin':
        return redirect('login')

    classes = Class.objects.all()
    sections = []
    students = []

    selected_class = None
    selected_section = None

    if request.method == 'POST':
        class_id = request.POST.get('class')
        section_id = request.POST.get('section')

        selected_class = class_id
        selected_section = section_id

        if class_id:
            sections = Section.objects.filter(class_name_id=class_id)

        if class_id and section_id:
            students = Student.objects.filter(
                student_class_id=class_id,
                section_id=section_id
            )

    return render(request, 'dashboard/admin/manage_students.html', {
        'classes': classes,
        'sections': sections,
        'students': students,
        'selected_class': selected_class,
        'selected_section': selected_section
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



@login_required
def manage_students(request):
    if request.user.role != 'data_entry':
        return redirect('login')

    students = Student.objects.all()

    return render(request, 'dashboard/data_entry/students.html', {
        'students': students
    })



@login_required
def add_student(request):
    if request.user.role != 'data_entry':
        return redirect('login')

    if request.method == 'POST':
        form = StudentForm(request.POST)

        if form.is_valid():
            # ✅ SAVE STUDENT
            student = form.save()

            # 🔥 CREATE APAAR PROFILE
            ApaarProfile.objects.create(student=student)

            # 🔥 AUDIT LOG (FIXED)
            log_action(
                request.user,
                "Added Student",
                "Student",
                student.id   # ✅ IMPORTANT FIX
            )

            return redirect('manage_students')

    else:
        form = StudentForm()

    # ✅ KEEP YOUR EXISTING LOGIC
    sections = Section.objects.all()

    return render(request, 'dashboard/data_entry/add_student.html', {
        'form': form,
        'sections': sections
    })

@login_required
def edit_student(request, student_id):
    if request.user.role not in ['admin', 'data_entry']:
        return redirect('login')

    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('manage_students')
    else:
        form = StudentForm(instance=student)

    #  ADD THIS
    sections = Section.objects.all()

    return render(request, 'dashboard/data_entry/edit_student.html', {
        'form': form,
        'sections': sections   #  THIS IS REQUIRED
    })




@login_required
def delete_student(request, pk):
    #  Allow both admin and data_entry
    if request.user.role not in ['admin', 'data_entry']:
        return redirect('login')

    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        student_id = student.id
        student.delete()

        #  AUDIT LOG
        log_action(
            request.user,
            "Deleted Student",
            "Student",
            student_id
        )

        #  Redirect based on role
        if request.user.role == 'admin':
            return redirect('admin_manage_students')
        else:
            return redirect('manage_students')

    # Optional confirmation page
    return render(request, 'dashboard/confirm_delete.html', {
        'student': student
    })
#=======Marks Entry By Teacher=================#
@login_required
def enter_marks(request):
    if request.user.role != 'teacher':
        return redirect('login')

    # 🔥 GET ALL SUBJECTS ASSIGNED TO TEACHER
    teacher_subjects = TeacherSubject.objects.filter(teacher=request.user)
    subjects = [ts.subject for ts in teacher_subjects]

    classes = Class.objects.all()
    sections = Section.objects.all()

    students = None
    existing_marks = {}
    selected_subject = None

    # ================= POST HANDLING ================= #
    if request.method == 'POST':

        subject_id = request.POST.get('subject')
        class_id = request.POST.get('class')
        section_id = request.POST.get('section')

        # 🔒 SAFE SUBJECT FETCH
        if subject_id:
            selected_subject = Subject.objects.filter(id=subject_id).first()

        # 🔒 ONLY PROCEED IF ALL REQUIRED VALUES EXIST
        if selected_subject and class_id and section_id:

            students = Student.objects.filter(
                student_class_id=class_id,
                section_id=section_id
            )

            # 🔥 LOAD EXISTING MARKS
            results = Result.objects.filter(
                subject=selected_subject,
                student__in=students
            )

            existing_marks = {
                r.student.id: r.marks for r in results
            }

            # 🔥 SAVE MARKS ONLY IF MARKS SUBMITTED
            for student in students:
                marks = request.POST.get(f'marks_{student.id}')

                # skip empty inputs
                if marks is None or marks == '':
                    continue

                try:
                    marks = int(marks)
                except ValueError:
                    continue

                Result.objects.update_or_create(
                    student=student,
                    subject=selected_subject,
                    defaults={
                        'teacher': request.user,
                        'marks': marks
                    }
                )
                log_action(
                 request.user,
                 f"Entered marks for {selected_subject}",
                  "Result",
                  student.id
                  )

    # ================= RESPONSE ================= #
    return render(request, 'dashboard/teacher/enter_marks.html', {
        'subjects': subjects,
        'classes': classes,
        'sections': sections,
        'students': students,
        'existing_marks': existing_marks,
        'selected_subject': selected_subject
    })


#=======RESULT OF ADMIN ================#
@login_required
def admin_results(request):
    if request.user.role != 'admin':
        return redirect('login')

    classes = Class.objects.all()
    sections = []
    selected_class = None
    selected_section = None
    student_data = []

    class_id = None
    section_id = None

    if request.method == 'POST':
        class_id = request.POST.get('class')
        section_id = request.POST.get('section')

    # 🔥 LOAD SECTIONS BASED ON CLASS
    if class_id:
        sections = Section.objects.filter(class_name_id=class_id)

    # 🔥 SUBJECT MAP
    subject_map = {
        "L1": "l1",
        "L2": "l2",
        "L3": "l3",
        "SCI": "science",
        "MATH": "mathematics",
        "SOC": "social_science"
    }

    if request.method == 'POST' and class_id and section_id:

        selected_class = class_id
        selected_section = section_id

        students = Student.objects.filter(
            student_class_id=class_id,
            section_id=section_id
        )

        for student in students:

            row = {
                'roll': student.roll_number,
                'name': student.name,
                'marks': {
                    'l1': 0,
                    'l2': 0,
                    'l3': 0,
                    'science': 0,
                    'mathematics': 0,
                    'social_science': 0,
                },
                'total': 0,
                'percentage': 0,
                'status': 'Not Evaluated'   # 🔥 DEFAULT
            }

            fail = False
            has_marks = False   # 🔥 IMPORTANT

            # 🔥 FETCH RESULTS
            results = Result.objects.filter(student=student)

            for r in results:
                subject_name = r.subject.name.strip().upper()
                key = subject_map.get(subject_name)

                if key:
                    row['marks'][key] = r.marks
                    has_marks = True

                    if r.marks < 33:
                        fail = True

            # 🔥 CALCULATE TOTAL
            total = sum(row['marks'].values())
            row['total'] = total

            # 🔥 CALCULATE PERCENTAGE
            row['percentage'] = round(total / len(subject_map), 2) if has_marks else 0

            # 🔥 FINAL STATUS LOGIC
            if not has_marks:
                row['status'] = "Not Evaluated"
            elif fail:
                row['status'] = "Fail"
            else:
                row['status'] = "Pass"

            student_data.append(row)

    return render(request, 'dashboard/admin/results.html', {
        'classes': classes,
        'sections': sections,
        'students': student_data,
        'selected_class': selected_class,
        'selected_section': selected_section
    })
from django.http import JsonResponse

def get_sections(request):
    class_id = request.GET.get('class_id')
    sections = Section.objects.filter(class_name_id=class_id)

    data = list(sections.values('id', 'name'))

    return JsonResponse(data, safe=False)

from django.http import HttpResponse
from openpyxl import Workbook

@login_required
def export_results_excel(request):
    if request.user.role != 'admin':
        return redirect('login')

    class_id = request.GET.get('class')
    section_id = request.GET.get('section')

    students = Student.objects.filter(
        student_class_id=class_id,
        section_id=section_id
    )

    subject_map = {
        "L1": "l1",
        "L2": "l2",
        "L3": "l3",
        "SCI": "science",
        "MATH": "mathematics",
        "SOC": "social_science"
    }

    wb = Workbook()
    ws = wb.active
    ws.title = "Results"

    # 🔥 HEADER
    ws.append([
        "Roll No", "Name",
        "L1", "L2", "L3",
        "Science", "Maths", "Social",
        "Total", "Percentage", "Status"
    ])

    for student in students:
        results = Result.objects.filter(student=student)

        marks = {v: 0 for v in subject_map.values()}
        fail = False

        for r in results:
            key = subject_map.get(r.subject.name)
            if key:
                marks[key] = r.marks
                if r.marks < 33:
                    fail = True

        total = sum(marks.values())
        percentage = round(total / 6, 2)
        status = "Fail" if fail else "Pass"

        ws.append([
            student.roll_number,
            student.name,
            marks['l1'],
            marks['l2'],
            marks['l3'],
            marks['science'],
            marks['mathematics'],
            marks['social_science'],
            total,
            percentage,
            status
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=results.xlsx'

    wb.save(response)
    return response





@login_required
def apaar_profile(request, student_id):
    if request.user.role not in ['admin', 'data_entry']:
        return redirect('login')

    # ✅ SAFE FETCH
    student = get_object_or_404(Student, id=student_id)
    apaar = get_object_or_404(ApaarProfile, student=student)

    # 🔥 SUBJECT MAP (based on your DB naming)
    subject_map = {
        "L1": "l1",
        "L2": "l2",
        "L3": "l3",
        "SCI": "science",
        "MATH": "mathematics",
        "SOC": "social_science"
    }

    # 🔥 FETCH RESULTS
    results = Result.objects.filter(student=student)

    # 🔥 INIT MARKS
    marks = {v: 0 for v in subject_map.values()}

    fail = False
    has_marks = False   # 🔥 IMPORTANT FLAG

    # 🔥 PROCESS RESULTS
    for r in results:
        subject_name = r.subject.name.strip().upper()
        key = subject_map.get(subject_name)

        if key:
            marks[key] = r.marks
            has_marks = True

            if r.marks < 33:
                fail = True

    # 🔥 CALCULATIONS
    total = sum(marks.values())
    percentage = round(total / len(subject_map), 2) if has_marks else 0

    # 🔥 FINAL STATUS LOGIC
    if not has_marks:
        status = "Not Evaluated"
    elif fail:
        status = "Fail"
    else:
        status = "Pass"

    # 🔥 CONTEXT
    context = {
        'student': student,
        'apaar': apaar,
        'marks': marks,
        'total': total,
        'percentage': percentage,
        'status': status
    }

    return render(request, 'dashboard/apaar_profile.html', context)



@login_required
def apaar_validation(request):
    if request.user.role != 'admin':
        return redirect('login')

    student = None
    apaar = None

    if request.method == 'POST':
        roll = request.POST.get('roll')

        print("INPUT ROLL:", roll)  # 🔍 DEBUG

        if roll:
            # 🔥 SAFE QUERY (IMPORTANT FIX)
            student = Student.objects.filter(
                roll_number__iexact=roll.strip()
            ).first()

            print("FOUND STUDENT:", student)  # 🔍 DEBUG

            if student:
                apaar = ApaarProfile.objects.filter(student=student).first()

    return render(request, 'dashboard/apaar_validation.html', {
        'student': student,
        'apaar': apaar
    })
