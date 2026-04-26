from django.shortcuts import render
from django.shortcuts import render
from student.models import Student
from results.models import Result

# Create your views here.
def home(request):
    return render(request, 'public/home.html')


def result_view(request):
     student = None
     results = None
     total = 0
     percentage = 0
     status = None

     if request.method == 'POST':
        roll = request.POST.get('roll_number', '').strip()

        student = Student.objects.filter(
            roll_number__iexact=roll
        ).first()

        if student:
            results = Result.objects.filter(student=student)

            total = sum(r.marks for r in results)

            subject_count = results.count()

            if subject_count > 0:
                percentage = total / subject_count

            # 🔥 PASS / FAIL (simple rule)
            status = "Pass"
            for r in results:
                if r.marks < 33:
                    status = "Fail"
                    break

     return render(request, 'public/result.html', {
        'student': student,
        'results': results,
        'total': total,
        'percentage': round(percentage, 2),
        'status': status
    })

#===========PDF OF RESULT================#
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def download_result_pdf(request, roll):
    student = Student.objects.filter(roll_number__iexact=roll).first()

    if not student:
        return HttpResponse("Student not found")

    results = Result.objects.filter(student=student)

    total = sum(r.marks for r in results)
    subject_count = results.count()
    percentage = total / subject_count if subject_count else 0

    status = "Pass"
    for r in results:
        if r.marks < 33:
            status = "Fail"
            break

    # 🔥 CREATE PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student.roll_number}_result.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()

    elements = []

    # ================= HEADER =================
    # ================= HEADER =================
    elements.append(Paragraph("<b>ABC Public School</b>", styles['Title']))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("<b>Result Processing System</b>", styles['Heading2']))
    elements.append(Spacer(1, 5))

    elements.append(Paragraph("Academic Report Card", styles['Heading3']))
    elements.append(Spacer(1, 20))

    # ================= STUDENT INFO =================
    student_info = [
        ["Name:", student.name],
        ["Roll No:", student.roll_number],
        ["Class:", str(student.student_class)],
        ["Section:", str(student.section)],
    ]

    info_table = Table(student_info, colWidths=[100, 300])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 20))

    # ================= MARKS TABLE =================
    data = [["Subject", "Marks"]]

    for r in results:
        data.append([str(r.subject), str(r.marks)])

    data.append(["Total", str(total)])
    data.append(["Percentage", f"{round(percentage,2)}%"])
    data.append(["Result", status])

    marks_table = Table(data, colWidths=[250, 150])

    marks_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('BACKGROUND', (0, -3), (-1, -1), colors.lightgrey),

        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(marks_table)
    elements.append(Spacer(1, 30))

    # ================= FOOTER =================
    elements.append(Paragraph("This is a system generated report.", styles['Normal']))

    doc.build(elements)

    return response