from datetime import date, timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from dateutil.relativedelta import relativedelta
from django.core.validators import RegexValidator



GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
]


class SessionYearModel(models.Model):
    id = models.AutoField(primary_key=True)
    session_start_year = models.DateField()
    session_end_year = models.DateField()
    objects = models.Manager()



# Overriding the Default Django Auth User and adding One More Field (user_type)
class CustomUser(AbstractUser):
    HOD = '1'
    STAFF = '2'
    STUDENT = '3'
    
    EMAIL_TO_USER_TYPE_MAP = {
        'hod': HOD,
        'staff': STAFF,
        'student': STUDENT
    }

    user_type_data = ((HOD, "HOD"), (STAFF, "Staff"), (STUDENT, "Student"))
    user_type = models.CharField(default=1, choices=user_type_data, max_length=10)


class AdminHOD(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()



class Courses(models.Model):
    id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class Subjects(models.Model):
    id =models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=255)
    course_id = models.ForeignKey(Courses, on_delete=models.CASCADE, default=1) #need to give defauult course
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class Staffs(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False) 
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    date_of_birth = models.DateField(null=True, blank=True)  # Teacher's date of birth
    age = models.IntegerField(editable=False)
    gender = models.CharField(max_length=20, choices= GENDER_CHOICES, default='other')
    date_of_joining = models.DateField(null=True, blank=True)  # Date when teacher joined the institution  
    # Qualifications
    qualifications = models.TextField(blank=True, null=True)  # Teacher's qualifications   
    # Subjects taught by the teacher (Many-to-Many relationship)
    subjects_taught = models.ManyToManyField(Subjects, related_name="teachers")   
    # Profile Picture (Optional)
    profile_pic = models.FileField(upload_to='media/teacher_pics/', blank=True, null=True)   
    # Bio (Optional)
    bio = models.TextField(blank=True, null=True)  
    # Active Status
    is_active = models.BooleanField(default=True)  # Whether the teacher is active or not
    # Auto-generated Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    objects = models.Manager()



# class Students(models.Model):
#     id = models.AutoField(primary_key=True)
#     admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
#     gender = models.CharField(max_length=50)
#     profile_pic = models.FileField()
#     address = models.TextField()
#     course_id = models.ForeignKey(Courses, on_delete=models.DO_NOTHING, default=1)
#     session_year_id = models.ForeignKey(SessionYearModel, null=True, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     objects = models.Manager()


class Students(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=False)
    middle_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=False)
    email = models.EmailField(unique=True)  
    contact_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=20, choices= GENDER_CHOICES, null=False,default='other')
    age = models.IntegerField(editable=False)
    profile_pic = models.FileField(upload_to='media/profile_pics/', blank=True, null=True)
    address = models.TextField()
    father_name = models.CharField(max_length=255, null=False)
    student_cnic = models.CharField(
        max_length=15, 
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{5}-\d{7}-\d{1}$',
                message="CNIC/B-form must be in the format 'XXXXX-XXXXXXX-X'."
            )
        ]
    )
    father_cnic = models.CharField(
        max_length=15, 
        validators=[
            RegexValidator(
                regex=r'^\d{5}-\d{7}-\d{1}$',
                message="Father's CNIC must be in the format 'XXXXX-XXXXXXX-X'."
            )
        ]
    )
    date_of_birth = models.DateField(null=False)
    roll_number = models.IntegerField(editable=False)
    registration_number = models.CharField(max_length=20, unique=True, editable=False)
    course_id = models.ForeignKey(Courses, on_delete=models.DO_NOTHING, default=1)
    session_year_id = models.ForeignKey(SessionYearModel, null=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)  # Whether the student is active or not   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    class Meta:
        unique_together = ('course_id', 'roll_number')

    def save(self, *args, **kwargs):
        if not self.roll_number:
            last_student = Students.objects.filter(class_id=self.course_id).order_by('roll_number').last()
            self.roll_number = last_student.roll_number + 1 if last_student else 1

        if not self.registration_number:
            current_year_suffix = str(date.today().year)[-2:]
            self.registration_number = f"STU-{current_year_suffix}-{self.roll_number:02d}"

        if self.date_of_birth:
            self.age = relativedelta(timezone.now().date(), self.date_of_birth).years

        super().save(*args, **kwargs)


class Attendance(models.Model):
    # Subject Attendance
    id = models.AutoField(primary_key=True)
    subject_id = models.ForeignKey(Subjects, on_delete=models.DO_NOTHING)
    attendance_date = models.DateField()
    session_year_id = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class AttendanceReport(models.Model):
    # Individual Student Attendance
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.DO_NOTHING)
    attendance_id = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class LeaveReportStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class LeaveReportStaff(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class FeedBackStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class FeedBackStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()



class NotificationStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class NotificationStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    stafff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class StudentResult(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE, default=1)
    subject_exam_marks = models.FloatField(default=0)
    subject_assignment_marks = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


#Creating Django Signals

# It's like trigger in database. It will run only when Data is Added in CustomUser model

@receiver(post_save, sender=CustomUser)
# Now Creating a Function which will automatically insert data in HOD, Staff or Student
def create_user_profile(sender, instance, created, **kwargs):
    # if Created is true (Means Data Inserted)
    if created:
        # Check the user_type and insert the data in respective tables
        if instance.user_type == 1:
            AdminHOD.objects.create(admin=instance)
        if instance.user_type == 2:
            Staffs.objects.create(admin=instance)
        if instance.user_type == 3:
            Students.objects.create(admin=instance, course_id=Courses.objects.get(id=1), session_year_id=SessionYearModel.objects.get(id=1), address="", profile_pic="", gender="")
    

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.adminhod.save()
    if instance.user_type == 2:
        instance.staffs.save()
    if instance.user_type == 3:
        instance.students.save()
    


