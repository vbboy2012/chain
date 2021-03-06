from django.shortcuts import render
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login as auth_login,logout as auto_logout
from django.contrib.auth.hashers import make_password, check_password
from .models import User,UserAddress,CoinLog,Config,Icolock,Contact
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from bitcoinrpc.authproxy import AuthServiceProxy
from .Token import Token
from django.conf import settings as django_settings
import random,decimal,requests,json,smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

# Create your views here.
token_confirm = Token(django_settings.SECRET_KEY)
def index(request):
    if request.user.is_authenticated:
        #检测充值
        useraddress = UserAddress.objects.filter(uid=request.user.id).filter(yt=1)
        for addr in useraddress:
            if addr.type == 1:  # 检测BTC钱包充值情况
                rpc_connection = AuthServiceProxy(
                    "http://{}:{}@{}:{}".format(django_settings.BITCOIN_USER, django_settings.BITCOIN_PASS,
                                                django_settings.BITCOIN_HOST, django_settings.BITCOIN_PORT))
                allReceive = rpc_connection.getreceivedbyaddress(addr.addr)
                if allReceive > 0:
                    alllog = CoinLog.objects.filter(addr=addr.addr).filter(type=1)
                    count = 0
                    for log in alllog:
                        count += log.money
                    money = allReceive - count
                    if money > 0:
                        CoinLog.objects.create(uid=addr.uid, addr=addr.addr, type=1, coin_type=1, money=money, fee=0)
                # 对比3次网络确认的BTC数量，予以确认
                threeOK = rpc_connection.getreceivedbyaddress(addr.addr, 3)
                if threeOK > 0:
                    alllog = CoinLog.objects.filter(addr=addr.addr).filter(type=1).filter(status=0)
                    count = 0
                    for log in alllog:
                        count += log.money
                    if threeOK == count:
                        for log in alllog:
                            log.status = 1
                            log.save()
                            addr.money += log.money
                            addr.save()
            elif addr.type == 2:  # 检测ETH
                url = 'http://106.14.196.162:8828'
                headers = {'content-type': 'application/json'}
                payload = {
                    "method": "eth_getBalance",
                    "params": [addr.addr, 'latest'],
                    "jsonrpc": "2.0",
                    "id": 0,
                }
                response = requests.post(
                    url, data=json.dumps(payload), headers=headers).json()
                wei = int(response['result'], 16)
                if wei > 0:
                    wei = wei / 1000 / 1000 / 1000 / 1000 / 1000 / 1000
                    alllog = CoinLog.objects.filter(addr=addr.addr).filter(type=1)
                    count = 0
                    for log in alllog:
                        count += log.money
                    money = wei - float(count)
                    if money > 0:
                        CoinLog.objects.create(uid=addr.uid, addr=addr.addr, type=1, coin_type=2,money=money, fee=0, status=1)
                        addr.money += decimal.Decimal(money)
                        addr.save()
        #查询用户资料
        btcczdz = UserAddress.objects.filter(uid=request.user.id).filter(yt=1).filter(type=1)[:1]
        ethczdz = UserAddress.objects.filter(uid=request.user.id).filter(yt=1).filter(type=2)[:1]
        risczdz = UserAddress.objects.filter(uid=request.user.id).filter(yt=1).filter(type=3)[:1]
        tbdzList = UserAddress.objects.filter(uid=request.user.id).filter(yt=2)
        czList = CoinLog.objects.filter(uid=request.user.id).filter(type=1)
        tbList = CoinLog.objects.filter(uid=request.user.id).filter(type=2)
        icoList = Icolock.objects.filter(uid=request.user.id)
        userinfo = User.objects.get(id=request.user.id)
        if not btcczdz:
            status = 0
        else:
            status = 1
        # 检查阶段ICO是否结束
        icoConfig = Config.objects.all()
        rateList = []
        i = 1
        for config in icoConfig:
            count = Icolock.objects.filter(type=i).count()
            rate = {'id': i, 'rate': round((config.icoCount / config.risCount * 100), 2), 'icoCount': config.icoCount, 'count': count}
            rateList.append(rate)
            i += 1
        return render(request, 'index.html', {'status': status, 'btcczdz': btcczdz, 'ethczdz':ethczdz,'risczdz':risczdz,'tbdzList': tbdzList, 'czList': czList, 'tbList': tbList, 'userinfo': userinfo, 'icoConfig': icoConfig,'rateList':rateList,'icoList':icoList})
    else:
        #检查阶段ICO是否结束
        icoConfig = Config.objects.all()
        rateList = []
        i = 1
        for config in icoConfig:
            count = Icolock.objects.filter(type=i).count()
            rate = {'id': i, 'rate': round((config.icoCount / config.risCount * 100), 2), 'icoCount': config.icoCount, 'count': count}
            rateList.append(rate)
            i += 1
        return render(request, 'index.html',
                      {'icoConfig': icoConfig, 'rateList':rateList})

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
                message = "\n".join([u'{0},欢迎加入RISChain'.format(cd['username']), u'请访问该链接，完成用户验证:',
                                     '/'.join([django_settings.DOMAIN, 'activate', token])])
                msg = MIMEText(message, 'plain', 'utf-8')
                msg['From'] = formataddr(["RISChain", django_settings.EMAIL_HOST_USER])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
                msg['To'] = formataddr(["FK", user.username])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
                msg['Subject'] = "RISChain用户注册验证!"  # 邮件的主题，也可以说是标题
                server = smtplib.SMTP_SSL(django_settings.EMAIL_HOST, django_settings.EMAIL_PORT)
                server.login(django_settings.EMAIL_HOST_USER, django_settings.EMAIL_HOST_PASSWORD)
                server.sendmail(django_settings.EMAIL_HOST_USER, [user.username], msg.as_string())
                server.quit()
                #send_mail('RISChain用户注册验证!', message, django_settings.EMAIL_HOST_USER, [cd['username']], fail_silently=False)
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
        message = "\n".join([u'{0},欢迎加入RISChain'.format(user.username), u'请访问该链接，完成用户验证:',
                             '/'.join([django_settings.DOMAIN, 'activate', token])])

        msg = MIMEText(message, 'plain', 'utf-8')
        msg['From'] = formataddr(["RISChain", django_settings.EMAIL_HOST_USER])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["FK", user.username])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "RISChain用户注册验证!"  # 邮件的主题，也可以说是标题
        server = smtplib.SMTP_SSL(django_settings.EMAIL_HOST, django_settings.EMAIL_PORT)
        server.login(django_settings.EMAIL_HOST_USER, django_settings.EMAIL_HOST_PASSWORD)
        server.sendmail(django_settings.EMAIL_HOST_USER, [user.username], msg.as_string())
        server.quit()
        #send_mail('RISChain用户注册验证!', message, django_settings.EMAIL_HOST_USER, [user.username], fail_silently=False)
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
        type = request.POST['tbtype']
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
            czdz = UserAddress.objects.filter(uid=request.user.id).filter(yt=1).filter(type=type)
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
                CoinLog.objects.create(uid=request.user.id, addr=tbdz, type=2, coin_type=type,money=tbcount, fee=tbfee)
                return JsonResponse('1', safe=False)
        else:
            return JsonResponse('2', safe=False)
    else:
        return JsonResponse('0', safe=False)

def canceltibi(request,id,type):
    if request.user.is_authenticated:
        id = int(id)
        type = int(type)
        coinlog = CoinLog.objects.get(id=id, uid=request.user.id)
        logmoney = coinlog.money
        logfee = coinlog.fee
        coinlog.status = 2
        coinlog.save()
        useraddress = UserAddress.objects.get(uid=request.user.id,type=type,yt=1)
        freenum = logmoney + logfee
        useraddress.money += freenum
        useraddress.frozen_num -= freenum
        useraddress.save()
    return HttpResponseRedirect('/')

def sendcode(request):
    seed = "1234567890"
    sa = []
    for i in range(4):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    request.session['tbcode'] = salt
    user = User.objects.get(id=request.user.id)
    message = "\n".join([u'您的验证码是：{0}'.format(salt)])
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['From'] = formataddr(["RISChain", django_settings.EMAIL_HOST_USER])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
    msg['To'] = formataddr(["FK", user.username])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
    msg['Subject'] = "RISChain添加提币地址验证!"  # 邮件的主题，也可以说是标题
    server = smtplib.SMTP_SSL(django_settings.EMAIL_HOST, django_settings.EMAIL_PORT)
    server.login(django_settings.EMAIL_HOST_USER, django_settings.EMAIL_HOST_PASSWORD)
    server.sendmail(django_settings.EMAIL_HOST_USER, [user.username], msg.as_string())
    server.quit()
    # send_mail('RISChain添加提币地址验证!', message, django_settings.EMAIL_HOST_USER, [user.username], fail_silently=False)
    return JsonResponse('1', safe=False)

def showinfo(request):
    if request.method == 'POST' and request.user.is_authenticated:
        #生成BTC地址
        rpc_connection = AuthServiceProxy(
            "http://{}:{}@{}:{}".format(django_settings.BITCOIN_USER, django_settings.BITCOIN_PASS,
                                        django_settings.BITCOIN_HOST, django_settings.BITCOIN_PORT))
        btcAddress = rpc_connection.getnewaddress(request.user.username)
        UserAddress.objects.create(uid=request.user.id, type=1, yt=1, addr=btcAddress, money=0, status=1)
        #生成ETH地址
        url = 'http://106.14.196.162:8828'
        headers = {'content-type': 'application/json'}
        payload = {
            "method": "personal_newAccount",
            "params": ["jzb198625"],
            "jsonrpc": "2.0",
            "id": 0,
        }
        btcAddress = requests.post(
            url, data=json.dumps(payload), headers=headers).json()
        UserAddress.objects.create(uid=request.user.id, type=2, yt=1, addr=btcAddress['result'], money=0, status=1)
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

def getreceive(request):
    if request.method == 'POST' and request.user.is_authenticated:
        useraddress = UserAddress.objects.filter(uid=request.user.id).filter(yt=1)
        for addr in useraddress:
            if addr.type == 1:      #检测BTC钱包充值情况
                rpc_connection = AuthServiceProxy(
                    "http://{}:{}@{}:{}".format(django_settings.BITCOIN_USER, django_settings.BITCOIN_PASS,
                                                django_settings.BITCOIN_HOST, django_settings.BITCOIN_PORT))
                allReceive = rpc_connection.getreceivedbyaddress(addr.addr)
                if allReceive > 0:
                    alllog = CoinLog.objects.filter(addr=addr.addr).filter(type=1)
                    count = 0
                    for log in alllog:
                        count += log.money
                    money = allReceive - count
                    if money > 0:
                        CoinLog.objects.create(uid=addr.uid, addr=addr.addr, type=1, coin_type=1,money=money, fee=0)
                #对比3次网络确认的BTC数量，予以确认
                threeOK = rpc_connection.getreceivedbyaddress(addr.addr, 3)
                if threeOK > 0:
                    alllog = CoinLog.objects.filter(addr=addr.addr).filter(type=1).filter(status=0)
                    count = 0
                    for log in alllog:
                        count += log.money
                    if threeOK == count:
                        for log in alllog:
                            log.status = 1
                            log.save()
                            addr.money += log.money
                            addr.save()
            elif addr.type == 2:    #检测ETH
                url = 'http://106.14.196.162:8828'
                headers = {'content-type': 'application/json'}
                payload = {
                    "method": "eth_getBalance",
                    "params": [addr.addr, 'latest'],
                    "jsonrpc": "2.0",
                    "id": 0,
                }
                response = requests.post(
                    url, data=json.dumps(payload), headers=headers).json()
                wei = int(response['result'], 16)
                if wei > 0:
                    wei = wei / 1000 / 1000 / 1000 / 1000 / 1000 / 1000
                    alllog = CoinLog.objects.filter(addr=addr.addr).filter(type=1)
                    count = 0
                    for log in alllog:
                        count += log.money
                    money = wei - float(count)
                    if money > 0:
                        CoinLog.objects.create(uid=addr.uid, addr=addr.addr, type=1, coin_type=2,money=money, fee=0, status=1)
                        addr.money += decimal.Decimal(money)
                        addr.save()
        return JsonResponse(count, safe=False)
    else:
        return JsonResponse('0', safe=False)


def icolock(request):
    if request.method == 'POST':
        # 检查资金密码
        safepass = request.POST['safepass']
        user = User.objects.get(id=request.user.id)
        if not check_password(safepass, user.safe_password):
            return JsonResponse('2', safe=False)
        # 检测资金是否充足
        icoStep = str(request.POST['icoStep']).split('-')

        # 判断是否ICO结束
        if icoStep[0] == 'step1':
            config = Config.objects.get(id=1)
        elif icoStep[0] == 'step2':
            config = Config.objects.get(id=2)
        elif icoStep[0] == 'step3':
            config = Config.objects.get(id=3)
        if config.icoCount >= config.risCount:
            return JsonResponse('5', safe=False)

        if icoStep[1] == 'btc':
            coin_type = 1
        elif icoStep[1] == 'eth':
            coin_type = 2

        money = float(request.POST['money'])
        useraddress = UserAddress.objects.filter(uid=request.user.id).filter(type=coin_type).filter(yt=1)[:1]
        for useradd in useraddress:
            if money > useradd.money:  # 可用资金不足
                return JsonResponse('3', safe=False)
            else:
                # 进入ICO环节
                if coin_type == 1:
                    ris = config.btcRate * money
                elif coin_type == 2:
                    ris = config.ethRate * money
                Icolock.objects.create(uid=request.user.id, addr=useradd.addr, type=config.id, coin_type=coin_type, money=money, ris=ris,status=1)
                config.icoCount += ris
                config.save()
                useradd.money -= decimal.Decimal(money)
                useradd.save()
                return JsonResponse("1", safe=False)
    else:
        return JsonResponse('0', safe=False)

def autoico(request,type):
    if request.user.is_authenticated and request.user.id == 1:
        config = Config.objects.get(id=type)
        money = random.randrange(1, 4, 1)
        ris = config.btcRate * money
        Icolock.objects.create(uid=request.user.id, addr='', type=type, coin_type=1, money=money, ris=ris)
        config.icoCount += ris
        config.save()
        return HttpResponse("random：" + str(money) + "--" + str(config.icoCount / config.risCount) + "%")
    return HttpResponse('0')

def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        Contact.objects.create(name=name, email=email, subject=subject, message=message)
        return JsonResponse('1', safe=False)
    else:
        return JsonResponse('0', safe=False)

# 测试函数
# walletpassphrase getreceivedbyaddress
def bitcoinrpc(request):
    rpc_connection = AuthServiceProxy(
        "http://{}:{}@{}:{}".format(django_settings.BITCOIN_USER, django_settings.BITCOIN_PASS,
                                    django_settings.BITCOIN_HOST, django_settings.BITCOIN_PORT))
    # user = User.objects.get(id=request.user.id)
    # useraddress = UserAddress.objects.get(uid=request.user.id, yt=1)
    address = rpc_connection.getreceivedbyaddress("115jcQWoGSEFf4xWcmsdj299wrULkEv4FQ")
    #address = rpc_connection.gettransaction()
    return JsonResponse(address, safe=False)

def eth(request):
    url = 'http://106.14.196.162:8828'
    headers = {'content-type': 'application/json'}
    payload = {
        "method": "eth_getBalance",
        "params": ['0xd9ecb2e8be0a4a8ae32677a04585cca438bd80eb', 'latest'],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()
    wei = int(response['result'], 16)
    if wei > 0:
       wei = wei / 1000 / 1000 / 1000 / 1000 / 1000 / 1000
    return JsonResponse(response, safe=False)
