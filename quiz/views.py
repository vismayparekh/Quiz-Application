from random import sample
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from .models import TeacherLogin, StudentLogin
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import QuizTable, Question, Choice, Answer, Results
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import ObjectDoesNotExist
from django.utils.timezone import now
from .models import TeacherLogin, QuizTable, Question, Choice, Answer
from django.db.models import Count, F
from django.db.models import Count, F, Value
from django.db.models.functions import Coalesce
def homepage(request):
    return render(request, 'Homepage.html')

def TeacherRegister(request):
    if request.method == "POST":
        TeacherUsername = request.POST.get('TeacherUsername')
        existing_teacher = TeacherLogin.objects.filter(TeacherUsername=TeacherUsername).first()
        if existing_teacher:
            return render(request, 'teachers.html', {'message': 'User already exists'})
        else:
            if request.POST.get('TeacherFirstName') and request.POST.get('TeacherLastName') and TeacherUsername and request.POST.get('TeacherPassword'):
                new_teacher = TeacherLogin()
                new_teacher.TeacherFirstName = request.POST.get('TeacherFirstName')
                new_teacher.TeacherLastName = request.POST.get('TeacherLastName')
                new_teacher.TeacherUsername = TeacherUsername
                new_teacher.TeacherPassword = request.POST.get('TeacherPassword')
                new_teacher.Subject =request.POST.get ('Subject')
                new_teacher.save()
                TeacherID = new_teacher.pk

                return render(request, 'teachers.html', {'TeacherID': TeacherID})

    return render(request, 'teachers.html')

def StudentRegister(request):
    if request.method == "POST":
        StuUsername = request.POST.get('StuUsername')
        existing_stu = StudentLogin.objects.filter(StuUsername=StuUsername).first()
        if existing_stu:
            return render(request, 'student.html', {'message': 'User already exists'})
        else:
            if request.POST.get('StuFirstName') and request.POST.get('StuLastName') and StuUsername and request.POST.get('StuPassword'):
                new_stu = StudentLogin()
                new_stu.StuFirstName = request.POST.get('StuFirstName')
                new_stu.StuLastName = request.POST.get('StuLastName')
                new_stu.StuUsername = StuUsername
                new_stu.StuPassword = request.POST.get('StuPassword')
                new_stu.save()
                StuID = new_stu.pk

                return render(request, 'student.html', {'StuID': StuID})

    return render(request, 'student.html')

def TeacherLoginView(request):
    if request.method == "POST":
        TeacherUsername = request.POST.get('TeacherUsername')
        TeacherPassword = request.POST.get('TeacherPassword')
        
        teacher = TeacherLogin.objects.filter(TeacherUsername=TeacherUsername).first()

        if teacher and teacher.TeacherPassword == TeacherPassword:
            # Authentication successful, redirect to the teacher's dashboard
            return redirect('quiz:teacher_dashboard', TeacherID=teacher.TeacherID)
        else:
            # Authentication failed, return an error message
            return render(request, 'teacher_login.html', {'teacher': teacher, 'message': 'Invalid username or password'})

    return render(request, 'teacher_login.html')

def StudentLoginView(request):
    if request.method == "POST":
        StuUsername = request.POST.get('StuUsername')
        StuPassword = request.POST.get('StuPassword')

        student = StudentLogin.objects.filter(StuUsername=StuUsername).first()

        if student and student.StuPassword == StuPassword:
            # Authentication successful, redirect to the student's dashboard
            return redirect('quiz:student_dashboard', StuID=student.StuID)
        else:
            # Authentication failed, return an error message
            return render(request, 'student_login.html', {'message': 'Invalid username or password'})

    return render(request, 'student_login.html')

def teacher_dashboard(request, TeacherID):
    # Retrieve quizzes for the teacher dashboard based on TeacherID
    quizzes = QuizTable.objects.filter(TID=TeacherID).all()
    return render(request, 'teacher_dashboard.html', {'quizzes': quizzes, 'TeacherID': TeacherID})

def view_quiz(request, quiz_id):
    quiz = get_object_or_404(QuizTable, id=quiz_id)
    questions = Question.objects.filter(quiz=quiz)
    
    # Retrieve choices and answers for each question
    question_details = []
    for question in questions:
        choices = Choice.objects.filter(question=question)
        answer = Answer.objects.get(question=question)
        question_details.append({'question': question, 'choices': choices, 'answer': answer})

    # You can add more data to context if needed
    context = {
        'quiz': quiz,
        'question_details': question_details,
    }

    return render(request, 'view_quiz.html', context)


def student_dashboard(request, StuID):
    student = StudentLogin.objects.get(StuID=StuID)
    quizzes = QuizTable.objects.values('Subject', 'QuizName', 'Deadline', 'MaxAttempts')

    # Retrieve quiz results for the student with attempts information
    results = Results.objects.filter(SID=student).annotate(attempts=Coalesce(Count('Qname'), Value(0)))

    # Update quizzes queryset to include attempts information
    for quiz in quizzes:
        # Get the initial attempts from the quiz results
        initial_attempts = results.filter(Qname__QuizName=quiz['QuizName']).first()

        # If the student is newly registered, use MaxAttempts as initial_attempts
        if initial_attempts is None:
            initial_attempts = quiz['MaxAttempts']
        else:
            # If the student has attempted the quiz, update initial_attempts to reflect actual attempts
            initial_attempts = initial_attempts.MaxAttempts

        # Include attempts information directly in the quizzes queryset
        quiz['initial_attempts'] = initial_attempts
        quiz['max_attempts'] = quiz['MaxAttempts']

    context = {
        'StuID': StuID,
        'student': student,
        'quizzes': quizzes,
        'results': results,
    }

    return render(request, 'student_dashboard.html', context)

def create_quiz(request):
    if request.method == 'POST':
        teacher_id = request.POST['teacher_id']
        quiz_name = request.POST['quiz_name']
        deadline = request.POST['deadline']  
        max_attempts = int(request.POST['max_attempts'])
        
        # Create the quiz with timestamp
        teacher = TeacherLogin.objects.get(TeacherID=teacher_id)
        quiz = QuizTable.objects.create(TID=teacher, QuizName=quiz_name, Subject=teacher.Subject, Timestamp=timezone.now(),Deadline=deadline,MaxAttempts=max_attempts)

        # Process questions, choices, and answers
        questions = request.POST.getlist('questions[]')

        # Ensure there are at least 10 questions
        if len(questions) < 10:
            return HttpResponseBadRequest("A quiz must have at least 10 questions.")

        choices_list = request.POST.getlist('choices[]')
        answers = request.POST.getlist('answers[]')

        for i, question_text in enumerate(questions):
            # Create a question for each iteration
            question = Question.objects.create(quiz=quiz, Ques=question_text)

            # Add choices for the question
            choices = choices_list[i * 4: (i + 1) * 4]
            Choice.objects.create(
                question=question,
                Choices1=choices[0],
                Choices2=choices[1],
                Choices3=choices[2],
                Choices4=choices[3]
            )

            # Add answer for the question
            Answer.objects.create(question=question, Ans=answers[i])

        # Redirect to the teacher dashboard after creating the quiz
        return redirect('quiz:teacher_dashboard', TeacherID=teacher_id)

    teachers = TeacherLogin.objects.all()
    return render(request, 'create_quiz.html', {'teachers': teachers})


def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(QuizTable, pk=quiz_id)

    if request.method == 'POST':
        # Handle the form submission for editing quiz details
        quiz_name = request.POST.get('quiz_name')
        quiz.QuizName = quiz_name

        # Update deadline and max attempts
        quiz.Deadline = request.POST.get('deadline')
        quiz.MaxAttempts = int(request.POST.get('max_attempts'))
        quiz.save()

        # Process questions, choices, and answers
        questions = request.POST.getlist('questions[]')

        # Ensure there are at least 10 questions
        if len(questions) < 10:
            return HttpResponseBadRequest("A quiz must have at least 10 questions.")

        choices_list = request.POST.getlist('choices[]')
        answers = request.POST.getlist('answers[]')

        # Clear existing questions not present in the submitted list
        existing_questions = quiz.question_set.all()
        for question in existing_questions:
            if question.Ques not in questions:
                question.delete()

        # Update or create questions, choices, and answers
        for i, question_text in enumerate(questions):
            question, created = Question.objects.get_or_create(quiz=quiz, Ques=question_text)

            # Handle choices if they exist
            choices = choices_list[i * 4: (i + 1) * 4]
            existing_choices = question.choice_set.all()

            for j, choice_text in enumerate(choices):
                choice, created = Choice.objects.get_or_create(question=question, defaults={
                    'Choices1': choices[0],
                    'Choices2': choices[1],
                    'Choices3': choices[2],
                    'Choices4': choices[3],
                })

                # Update existing choices if they exist
                if not created:
                    choice.Choices1 = choices[0]
                    choice.Choices2 = choices[1]
                    choice.Choices3 = choices[2]
                    choice.Choices4 = choices[3]
                    choice.save()

            # Handle answers if they exist
            try:
                answer = question.answer_set.get()
                answer.Ans = answers[i]
                answer.save()
            except Answer.DoesNotExist:
                # If the answer does not exist, create a new one
                Answer.objects.create(question=question, Ans=answers[i])

        # Redirect to the teacher dashboard after editing the quiz
        return redirect('quiz:teacher_dashboard', TeacherID=quiz.TID.TeacherID)

    # Include teacher_id in the context when rendering the template
    teacher_id = quiz.TID.TeacherID
    return render(request, 'edit_quiz.html', {'quiz': quiz, 'teacher_id': teacher_id})

def delete_quiz(request, quiz_id, teacher_id):
    quiz = get_object_or_404(QuizTable, pk=quiz_id)

    if request.method == 'POST':
        # Handle the form submission for deleting the quiz
        quiz.delete()

        return redirect('quiz:teacher_dashboard', TeacherID=teacher_id)

    return render(request, 'delete_quiz.html', {'quiz': quiz, 'teacher_id': teacher_id})


def take_quiz(request, stu_id, quiz_name):
    if request.method == 'POST':
        stu_id = int(request.POST.get('stu_id'))
        quiz_id = int(request.POST.get('quiz_id'))
        quiz = QuizTable.objects.get(id=quiz_id)


        # Check if the quiz has not expired and the student has attempts left
        if quiz.Deadline >= timezone.now() and quiz.MaxAttempts >= 0:
            quiz.MaxAttempts -= 1
            quiz.save()

            # Retrieve all questions for the chosen quiz
            all_questions = Question.objects.filter(quiz=quiz)

            # Randomly select 5 questions
            selected_questions = sample(list(all_questions), min(5, len(all_questions)))

            # Initialize the score
            score = 0

            # Your existing logic for taking the quiz and calculating the score
            for question in selected_questions:
                # Get the correct answer for the question
                correct_answer = Answer.objects.get(question=question).Ans

                # Get the student's response from the form submission
                student_response = request.POST.get('question_' + str(question.id))

                # Check each choice field against the correct answer
                if student_response == correct_answer:
                    score += 1

            # Update the student's score in the database
            student = StudentLogin.objects.get(StuID=stu_id)
            Results.objects.create(SID=student, Qname=quiz, Score=score)

            # Redirect to a confirmation page or any other appropriate action
            return redirect('quiz:show_results', stu_id=stu_id)
        else:
            result_message = "Quiz has expired or you have no attempts left."
            return render(request, 'take_quiz.html', {'result_message': result_message})

    else:
        try:
            quiz = QuizTable.objects.get(QuizName=quiz_name)

            # Check if the quiz has attempts left
            if quiz.MaxAttempts > 0:
                questions = Question.objects.filter(quiz=quiz)
                choices = Choice.objects.filter(question__in=questions)
                selected_questions = sample(list(questions), min(5, len(questions)))

                return render(request, 'take_quiz.html', {'stu_id': stu_id, 'quiz_name': quiz_name, 'quiz': quiz, 'questions': selected_questions, 'choices': choices})
            else:
                result_message = "Quiz attempts are exhausted."
                return render(request, 'take_quiz.html', {'result_message': result_message})

        except QuizTable.DoesNotExist:
            result_message = "Quiz not found."
            return render(request, 'take_quiz.html', {'result_message': result_message})



    
    
def show_results(request, stu_id):
    # Retrieve the student's results
    results = Results.objects.filter(SID_id=stu_id)

    return render(request, 'show_results.html', {'results': results})