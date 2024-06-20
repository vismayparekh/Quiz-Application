from django.db import models
from django.utils import timezone
import random

def generate_user_id():
    while True:
        user_id = random.randint(10000000, 99999999)
        if user_id not in TeacherLogin.objects.values_list('TeacherID') and user_id not in StudentLogin.objects.values_list('StuID'):
            return user_id

class TeacherLogin(models.Model):
    TeacherFirstName = models.CharField(max_length=50)
    TeacherLastName = models.CharField(max_length=50)
    TeacherUsername = models.CharField(max_length=30, unique=True)
    TeacherID = models.AutoField( primary_key=True, default=generate_user_id)
    TeacherPassword = models.CharField(max_length=255, default="default_password")
    Subject = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'TeacherLogin'

class StudentLogin(models.Model):
    StuFirstName = models.CharField(max_length=50)
    StuLastName = models.CharField(max_length=50)
    StuUsername = models.CharField(max_length=30, unique=True)
    StuID = models.AutoField( primary_key=True, default=generate_user_id)
    StuPassword = models.CharField(max_length=255, default="default_password")  
    
    class Meta:
        db_table = 'StudentLogin'

class QuizTable(models.Model):
    Subject = models.CharField(max_length=200)
    TID = models.ForeignKey(TeacherLogin, on_delete=models.CASCADE)
    QuizName = models.CharField(max_length=100,unique=True)
    Timestamp = models.DateTimeField(default=timezone.now)
    Deadline = models.DateTimeField()
    MaxAttempts = models.PositiveIntegerField(default=1)
    def is_expired(self):
        return timezone.now() > self.Deadline
    
    class Meta:
       db_table = 'Quizzzz'


       
class Question(models.Model):
    Ques = models.CharField(max_length=1000)
    QuesType = models.CharField(max_length=20, choices=[('single_choice', 'Single Choice'), ('multiple_choice', 'Multiple Choice'), ('short_answer', 'Short Answer'), ('true_false', 'True/False')])
    quiz = models.ForeignKey('QuizTable', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Question'  

class Choice(models.Model):
    Choices1 = models.CharField(max_length=200)
    Choices2 = models.CharField(max_length=200)
    Choices3 = models.CharField(max_length=200)
    Choices4 = models.CharField(max_length=200)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Choice'


class Answer(models.Model):
    Ans = models.CharField(max_length=200)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Answer'

class Results(models.Model):
    SID = models.ForeignKey(StudentLogin, on_delete=models.CASCADE)
    Qname = models.ForeignKey(QuizTable,on_delete=models.CASCADE)
    Score = models.IntegerField()
    DateTime = models.DateTimeField(default=timezone.now)
    MaxAttempts = models.PositiveIntegerField(default=1)
    
    class Meta:
        db_table='Results'





