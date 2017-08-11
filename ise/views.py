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
import random

# Create your views here.
token_confirm = Token(django_settings.SECRET_KEY)
def index(request):
    if request.user.is_authenticated:
        czdz = UserAddress.objects.filter(uid=request.user.id).filter(yt=1)[:1]
        tbdzList = UserAddress.objects.filter(uid=request.user.id).filter(yt=2)
        czList = CoinLog.objects.filter(uid=request.user.id).filter(type=1)
        tbList = CoinLog.objects.filter(uid=request.user.id).filter(type=2)
        userinfo = User.objects.get(id=request.user.id)
        if not czdz:
            status = 0
        else:
            status = 1
        return render(request, 'index.html', {'status': status, 'czdz': czdz, 'tbdzList': tbdzList, 'czList': czList, 'tbList': tbList, 'userinfo': userinfo})
    else:
        return render(request, 'index.html')

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
                message = "\n".join([u'{0},欢迎加入RISE'.format(cd['username']), u'请访问该链接，完成用户验证:',
                                     '/'.join([django_settings.DOMAIN, 'activate', token])])
                send_mail('RISEChain用户注册验证!', message, 'vbboy2012@163.com', [cd['username']], fail_silently=False)
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

def logout(request):
    auto_logout(request)
    return HttpResponseRedirect('/')

def active_user(request, token):
    try:
        username = token_confirm.confirm_validate_token(token)
    except:
        return render(request, 'message.html', {'message': 1})
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, 'message.html', {'message': 2})
    user.checkEmail = True
    user.save()
    return render(request, 'message.html', {'message': 3})

def checkmail(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)
        token = token_confirm.generate_validate_token(user.username)
        message = "\n".join([u'{0},欢迎加入RISE'.format(user.username), u'请访问该链接，完成用户验证:',
                             '/'.join([django_settings.DOMAIN, 'activate', token])])
        send_mail('RISEChain用户注册验证!', message, 'vbboy2012@163.com', [user.username], fail_silently=False)
        return JsonResponse('1', safe=False)
    else:
        return JsonResponse('0', safe=False)

def addaddress(request):
    if request.method == 'POST':
        pass2 = request.POST['pass2']
        user = User.objects.get(id=request.user.id)
        code = request.POST['code']
        try:
            tbcode = request.session['tbcode']
        except KeyError:
            return JsonResponse('3', safe=False)
        if code != tbcode:
            return JsonResponse('3', safe=False)
        if check_password(pass2, user.safe_password):
            del request.session['tbcode']
            type = request.POST['type']
            address = request.POST['addr']
            remark = request.POST['remark']
            UserAddress.objects.create(uid=request.user.id, type=type, yt=2, addr=address, money=0, remark=remark ,status=1)
            return JsonResponse('1', safe=False)
        else:
            return JsonResponse('2', safe=False)
    else:
        return JsonResponse('0', safe=False)

def tibi(request):
    if request.method == 'POST':
        pass2 = request.POST['tbpass2']
        user = User.objects.get(id=request.user.id)
        code = request.POST['tbcode']
        try:
            tbcode = request.session['tbcode']
        except KeyError:
            return JsonResponse('3', safe=False)
        if code != tbcode:
            return JsonResponse('3', safe=False)
        if check_password(pass2, user.safe_password):
            #del request.session['tbcode']
            #查询账号余额
            tbcount = float(request.POST['tbcount'])
            tbfee = float(request.POST['tbfee'])
            # rpc_connection = AuthServiceProxy(
            #     "http://{}:{}@{}:{}".format(django_settings.BITCOIN_USER, django_settings.BITCOIN_PASS,
            #                                 django_settings.BITCOIN_HOST, django_settings.BITCOIN_PORT))
            # rpc_connection.walletpassphrase("z35580113", 60)
            # balance = rpc_connection.getbalance(user.username)
            czdz = UserAddress.objects.filter(uid=request.user.id).filter(yt=1)[:1]
            balance = 0
            user_addr = ''
            for dz in czdz:
                balance = float(dz.money)
                user_addr = dz.addr
            tbcount -= tbfee
            if balance < tbcount:   #余额小于提币数量
                return JsonResponse('4', safe=False)
            else:
                tbdz = request.POST['tbdz']
                #扣除提币数量，冻结, 创建提币记录 待审核
                useraddress = UserAddress.objects.get(addr=user_addr)
                useraddress.money = balance-(tbcount+tbfee)
                useraddress.frozen_num = tbcount+tbfee
                useraddress.save()
                CoinLog.objects.create(uid=request.user.id, addr=tbdz, type=2, money=tbcount, fee=tbfee)
                return JsonResponse('1', safe=False)
        else:
            return JsonResponse('2', safe=False)
    else:
        return JsonResponse('0', safe=False)

def sendcode(request):
    seed = "1234567890abcdefghijklmnopqrstuvwxyz"
    sa = []
    for i in range(4):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    request.session['tbcode'] = salt
    user = User.objects.get(id=request.user.id)
    message = "\n".join([u'您的验证码是：{0}'.format(salt)])
    send_mail('RISEChain添加提币地址验证!', message, 'vbboy2012@163.com', [user.username], fail_silently=False)
    return JsonResponse('1', safe=False)

def showinfo(request):
    if request.method == 'POST':
        rpc_connection = AuthServiceProxy(
            "http://{}:{}@{}:{}".format(django_settings.BITCOIN_USER, django_settings.BITCOIN_PASS,
                                        django_settings.BITCOIN_HOST, django_settings.BITCOIN_PORT))
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
# walletpassphrase getreceivedbyaddress s
def bitcoinrpc(request):
    rpc_connection = AuthServiceProxy(
        "http://{}:{}@{}:{}".format(django_settings.BITCOIN_USER, django_settings.BITCOIN_PASS,
                                    django_settings.BITCOIN_HOST, django_settings.BITCOIN_PORT))
  #  user = User.objects.get(id=request.user.id)
    rpc_connection.walletpassphrase("z35580113",51)
    address = rpc_connection.getbalance()
    return JsonResponse(address,safe=False)

def test(request):
    result = UserAddress.objects.filter(uid=request.user.id)[:1]
    return render(request,'test.html',{'dataList':result})