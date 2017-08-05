from django.shortcuts import render
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login as auth_login,logout as auto_logout
from django.contrib.auth.models import User
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse

# Create your views here.

def index(request):
    return render(request,'index.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if len(User.objects.filter(username=cd['username'])):
                result = '用户名已经存在'
                return JsonResponse(result,safe=False)
            elif len(User.objects.filter(email=cd['email'])):
                return JsonResponse('email is have')
            else:
                user = User.objects.create_user(username=cd['username'], password=cd['password1'], email=cd['email'])
                user.save()
                return HttpResponse('Register successfully')
    else:
        form = LoginForm()
    return render(request, 'index.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    return JsonResponse('登录成功',safe=False)
                else:
                    return JsonResponse('登录失败', safe=False)
            else:
                return JsonResponse('账号或密码错误', safe=False)
        else:
            return JsonResponse('验证失败', safe=False)
    else:
        form = LoginForm()
        return render(request, 'index.html', {'form': form})

def logout(request):
    auto_logout(request)
    return render(request, 'index.html')