from results.models import Result
from .models import FraudAlert
from django.db.models import Avg, Count


def detect_fraud():

    #  CLEAR OLD ALERTS
    FraudAlert.objects.all().delete()

    results = Result.objects.select_related('student', 'subject')

    # ===============================
    #  STUDENT LEVEL DETECTION
    # ===============================
    for r in results:

        marks = r.marks
        student = r.student
        subject = r.subject

        #  HIGH MARKS
        if marks >= 95:
            FraudAlert.objects.create(
                student=student,
                subject=subject,
                marks=marks,
                issue="High Marks",
                risk_level="Medium"
            )

        #  FAIL MARKS
        if marks < 33:
            FraudAlert.objects.create(
                student=student,
                subject=subject,
                marks=marks,
                issue="Fail Marks",
                risk_level="Low"
            )

        #  SUDDEN JUMP (APAAR BASED)
        previous_avg = Result.objects.filter(
            student=student
        ).exclude(id=r.id).aggregate(avg=Avg('marks'))['avg']

        if previous_avg and marks > previous_avg + 30:
            FraudAlert.objects.create(
                student=student,
                subject=subject,
                marks=marks,
                issue="Sudden Performance Jump",
                risk_level="High"
            )

    # ===============================
    #  CLASS LEVEL DETECTION
    # ===============================

    # Same marks pattern
    duplicates = Result.objects.values(
        'subject_id', 'marks'
    ).annotate(count=Count('id')).filter(count__gte=5)

    for d in duplicates:
        FraudAlert.objects.create(
            issue="Same Marks Pattern Detected",
            risk_level="High",
            extra_info=f"Subject ID {d['subject_id']} → {d['count']} students scored {d['marks']}"
        )

    # ===============================
    #  TEACHER LEVEL DETECTION
    # ===============================

    # Teacher bias (high average marks)
    teacher_avg = Result.objects.values(
        'subject_id'
    ).annotate(avg_marks=Avg('marks'))

    for t in teacher_avg:
        if t['avg_marks'] and t['avg_marks'] > 85:
            FraudAlert.objects.create(
                issue="Teacher Bias (High Average Marks)",
                risk_level="Medium",
                extra_info=f"Subject ID {t['subject_id']} → Avg {round(t['avg_marks'],2)}"
            )