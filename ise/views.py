from django.shortcuts import render
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login as auth_login,logout as auto_logout
from django.contrib.auth.models import User
from .models import UserAddress,CoinLog
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from bitcoinrpc.authproxy import AuthServiceProxy,JSONRPCException
import json

# Create your views here.

def index(request):
    if request.user.is_authenticated:
        result = UserAddress.objects.filter(uid=request.user.id).filter(yt=1)[:1]
        result2 = UserAddress.objects.filter(uid=request.user.id).filter(yt=2)[:1]
        czList = CoinLog.objects.filter(uid=request.user.id).filter(type=1)
        tbList = CoinLog.objects.filter(uid=request.user.id).filter(type=2)
        if not result:
            status = 0
        else:
            status = 1
        return render(request, 'index.html', {'status': status, 'czdz': result, 'tbdz': result2,'czList': czList, 'tbList': tbList})
    else:
        return render(request,'index.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if len(User.objects.filter(username=cd['username'])):
                result = '1'
                return JsonResponse(result,safe=False)
            else:
                user = User.objects.create_user(username=cd['username'], password=cd['password1'])
                user.save()
                #Login
                auth_login(request, user)
                return JsonResponse('2',safe=False)
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
                    return JsonResponse('1',safe=False)
                else:
                    return JsonResponse('2', safe=False)
            else:
                return JsonResponse('3', safe=False)
        else:
            return JsonResponse('4', safe=False)
    else:
        form = LoginForm()
        return render(request, 'index.html', {'form': form})

def logout(request):
    auto_logout(request)
    return HttpResponseRedirect('/')

def showinfo(request):
    if request.method == 'POST':
        rpc_connection = AuthServiceProxy("http://vbboy2012:Okfuckyou123@106.14.155.141:8332")
        address = rpc_connection.getnewaddress(request.user.username)
        UserAddress.objects.create(uid=request.user.id, type=1,yt=1, addr=address, money=0, status=1)
        return JsonResponse('1', safe=False)
    else:
        return JsonResponse('0', safe=False)

def bitcoinrpc(request):
    rpc_connection = AuthServiceProxy("http://vbboy2012:Okfuckyou123@106.14.155.141:8332")
    address = rpc_connection.getnewaddress(request.user.username)
    UserAddress.objects.create(uid=request.user.id,type=1,addr=address,money=0,status=1)
    return JsonResponse(address,safe=False)

def test(request):
    result = UserAddress.objects.filter(uid=request.user.id)[:1]
    return render(request,'test.html',{'dataList':result})