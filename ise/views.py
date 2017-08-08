from django.shortcuts import render
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login as auth_login,logout as auto_logout
from django.contrib.auth.hashers import make_password, check_password
from .models import User,UserAddress,CoinLog
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from bitcoinrpc.authproxy import AuthServiceProxy,JSONRPCException
from django.core.mail import send_mail
from .Token import Token
from django.conf import settings as django_settings

# Create your views here.
token_confirm = Token(django_settings.SECRET_KEY)
def index(request):
    if request.user.is_authenticated:
        result = UserAddress.objects.filter(uid=request.user.id).filter(yt=1)[:1]
        result2 = UserAddress.objects.filter(uid=request.user.id).filter(yt=2)[:1]
        czList = CoinLog.objects.filter(uid=request.user.id).filter(type=1)
        tbList = CoinLog.objects.filter(uid=request.user.id).filter(type=2)
        userinfo = User.objects.get(id=request.user.id)
        if not result:
            status = 0
        else:
            status = 1
        return render(request, 'index.html', {'status': status, 'czdz': result, 'tbdz': result2,'czList': czList, 'tbList': tbList, 'userinfo': userinfo})
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
                token = token_confirm.generate_validate_token(cd['username'])
                message = "\n".join([u'{0},欢迎加入我的博客'.format(cd['username']), u'请访问该链接，完成用户验证:',
                                     '/'.join([django_settings.DOMAIN, 'activate', token])])
                send_mail('RISEChain共享经济体用户注册验证!', message, 'vbboy2012@163.com', [cd['username']], fail_silently=False)
                #Login
                auth_login(request, user)
                return JsonResponse('2', safe=False)
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

def active_user(request, token):
    try:
        username = token_confirm.confirm_validate_token(token)
    except:
        token_confirm.remove_validate_token(token)
        return render(request, 'message.html', {'message': u"对不起，验证链接已经超时，请重新发送邮件"})
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, 'message.html', {'message': u"对不起，您所验证的用户不存在，请重新注册"})
    user.checkEmail = True
    user.save()
    message = u'验证成功！'
    return render(request, 'message.html', {'message': message})

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

def setsafepass(request):
    if request.method == 'POST':
        ps = request.POST['safepass1']
        jm_ps = make_password(ps,None,'pbkdf2_sha256')
        User.objects.filter(id=request.user.id).update(safe_password=jm_ps)
        return JsonResponse('1', safe=False)
    else:
        return JsonResponse('0', safe=False)

def changepass(request):
    if request.method == 'POST':
        oldpass = request.POST['oldpass']
        type = request.POST['type']
        user = User.objects.get(id=request.user.id)
        if type == '1':
            if check_password(oldpass, user.password):
                ps = request.POST['newpass1']
                jm_ps = make_password(ps, None, 'pbkdf2_sha256')
                User.objects.filter(id=request.user.id).update(password=jm_ps)
                return JsonResponse('1', safe=False)
            else:
                return JsonResponse('2', safe=False)
        elif type == '2':
            if check_password(oldpass, user.safe_password):
                ps = request.POST['newpass1']
                jm_ps = make_password(ps, None, 'pbkdf2_sha256')
                User.objects.filter(id=request.user.id).update(safe_password=jm_ps)
                return JsonResponse('1', safe=False)
            else:
                return JsonResponse('2', safe=False)
        else:
            return JsonResponse('3', safe=False)

    else:
        return JsonResponse('0', safe=False)

#测试函数
def bitcoinrpc(request):
    rpc_connection = AuthServiceProxy("http://vbboy2012:Okfuckyou123@106.14.155.141:8332")
    address = rpc_connection.getnewaddress(request.user.username)
    UserAddress.objects.create(uid=request.user.id,type=1,addr=address,money=0,status=1)
    return JsonResponse(address,safe=False)

def test(request):
    result = UserAddress.objects.filter(uid=request.user.id)[:1]
    return render(request,'test.html',{'dataList':result})