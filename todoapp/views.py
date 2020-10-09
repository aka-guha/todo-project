from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from .form import TodoForm
from .models import Todo

def home(request):
    return render(request, 'todoapp/home.html')

def signupuser(request):
    if request.method =='GET':
        return render(request, 'todoapp/signupuser.html', {'form':UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                newuser = User.objects.create_user(request.POST['username'], password = request.POST['password1'])
                newuser.save()
                login(request,newuser)
                return redirect('currenttodo')
            except IntegrityError: 
                 return render(request, 'todoapp/signupuser.html', {'form':UserCreationForm(), 'error':'Username is already taken'})
        else:
            return render(request, 'todoapp/signupuser.html', {'form':UserCreationForm(), 'error':'Passwords did not match'})

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
        
def loginuser(request):
     if request.method =='GET':
        return render(request, 'todoapp/loginuser.html', {'form':AuthenticationForm()})
     else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todoapp/loginuser.html', {'form':AuthenticationForm(), 'error': 'User Not Found'})
        else:
            login(request,user)
            return redirect('currenttodo')

@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todoapp/createtodo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect ('currenttodo')
        except ValueError:
            return render(request, 'todoapp/createtodo.html', {'form': TodoForm(), 'error':'Unaccepted entry in title field'})

@login_required
def currenttodo(request):
    todos = Todo.objects.filter(user=request.user, completedon__isnull=True)
    return render(request, 'todoapp/currenttodo.html', {'todos': todos})

@login_required
def viewtodo(request, todo_pk):
    usertodos = get_object_or_404(Todo, pk=todo_pk, user = request.user)
    if request.method == 'GET':
        form = TodoForm(instance = usertodos)
        return render (request, 'todoapp/viewtodo.html', {'usertodo': usertodos, 'form': form})
    else:
        try:
            form = TodoForm(request.POST,instance = usertodos)
            form.save()
            return redirect ('currenttodo')
        except ValueError:
            return render (request, 'todoapp/viewtodo.html', {'usertodo': usertodos, 'error':'Error in action'})

@login_required
def completetodo(request,todo_pk):
    usertodo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
            usertodo.completedon = timezone.now()
            usertodo.save()
            return redirect('currenttodo')

@login_required
def deletetodo(request,todo_pk):
    usertodo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
            usertodo.delete()
            return redirect('currenttodo')

@login_required
def completedtodo(request):
    todos = Todo.objects.filter(user=request.user, completedon__isnull = False).order_by('-completedon')
    return render(request, 'todoapp/completedtodo.html', {'todos': todos})