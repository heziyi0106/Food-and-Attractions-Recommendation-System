from django.shortcuts import render, redirect
import hashlib, uuid, re
from django.contrib.sessions.models import Session
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.utils import timezone 
from account.forms import RegistrationForm
from account.models import *
from member_management.models import Points
from lineBot.models import LineAccountLink
from datetime import timezone as dt_timezone
from django.template import RequestContext


def login(request):
    if request.method == 'GET':
        return render(request, 'account/login.html', context={})
    elif request.method == 'POST':
        useraccount = request.POST["useraccount"]
        userpassword = request.POST["userpassword"]
        try:
            referer_url = request.META.get('HTTP_REFERER')
            pattern = r'linkToken=([A-Za-z0-9]+)'
            linktoken = re.search(pattern, referer_url).group(1)
        except:
            linktoken = False
        try:
            results = Webusers.objects.get(account=useraccount, password=userpassword, is_active='1')
        except:
            return render(request, 'account/login.html', context={'login': f'帳號或密碼錯誤'})

        if linktoken:
            nonce = uuid.uuid4()

            sql = LineAccountLink()
            sql.user_id = results.user_id 
            sql.nonce = nonce
            sql.lineid = ''
            sql.save()

            return redirect(f"https://access.line.me/dialog/bot/accountLink?linkToken={linktoken}&nonce={nonce}")

        elif results.username:
            request.session['name'] = results.account
            return redirect('/')
        else:
            return render(request, 'account/login.html', context={'login': f'帳號或密碼錯誤'})

def logout(request):
    if 'name' in request.session:
        del request.session['name']
    return redirect("/account/login")  #重新導向至 /
    
def register(request):
    if request.method == 'GET':
        return render(request, 'account/register.html')
    elif request.method == 'POST':    

        form = RegistrationForm(request.POST, request.FILES)
        print(form.is_valid())
        if form.is_valid():  #註冊檢查
            context_dict = {'userreuse':0,'password':0,'emailreuse':0,'phonereuse':0,
                'male':'','female':'','other':'',
                'account': form.cleaned_data["account"],
                'username': form.cleaned_data["username"],
                'gender': form.cleaned_data["gender"],
                'birthday': str(form.cleaned_data["birthday"]),
                'email': form.cleaned_data["email"],
                'phone': form.cleaned_data["phone"]}
                
            if Webusers.objects.filter(account=form.cleaned_data["account"]).exists():
                context_dict['userreuse'] = 1
                context_dict['account'] = ''
            if Webusers.objects.filter(email=form.cleaned_data["email"]).exists():
                context_dict['emailreuse'] = 1
                context_dict['email'] = ''
            if Webusers.objects.filter(phone=form.cleaned_data["phone"]).exists():
                context_dict['phonereuse'] = 1
                context_dict['phone'] = ''
            if form.cleaned_data["password"] != form.cleaned_data["confirm_password"]:
                context_dict['password'] = 1
            if form.cleaned_data["gender"] == 'F':
                context_dict['female'] = 'checked'
            elif form.cleaned_data["gender"] == 'M':
                context_dict['male'] = 'checked'
            elif form.cleaned_data["gender"] == 'O':
                context_dict['other'] = 'checked'
        
            if 1 in context_dict.values():
                print(context_dict)
                return render(request, 'account/register.html', context=context_dict)
            
            #檢查OK，寫入SQL
            sql = Webusers()
            sql.account = form.cleaned_data["account"]
            sql.password = form.cleaned_data["password"]
            sql.username = form.cleaned_data["username"]
            sql.gender = form.cleaned_data["gender"]
            sql.birthday = form.cleaned_data["birthday"]
            sql.email = form.cleaned_data["email"]
            sql.phone = form.cleaned_data["phone"]
            sql.save()
            
        else:
            print('error')

        # try:
        print(f'=={form.cleaned_data["email"]}==')
        user_id = Webusers.objects.get(email=form.cleaned_data["email"]).user_id
        if user_id:
            verify_token = hashlib.sha256(str(uuid.uuid4()).encode('utf-8')).hexdigest()  #製作token

            current_time = datetime.now()  #取得當前時間
            new_time = current_time + timedelta(hours=8,minutes=10)  #增加10分鐘
            formatted_time = new_time.strftime("%Y-%m-%d %H:%M:%S")  #格式化時間
  
            RegisterVerify(account_id_id=user_id, token_expiration=formatted_time, verify_token=verify_token).save()

            print('token ok')
            mailcontent = f'請點選下方連結啟用帳號' + '\n' + f'http://travel.yiiii.org/account/registerverify/?key={verify_token}'
            send_mail('啟用帳號', mailcontent, "0988118277y@gmail.com", [form.cleaned_data["email"]]) 
            print('mail success')
            
            sql = Points()
            sql.user_id = user_id
            sql.havepoint = 0
            sql.todaypoint = 0
            sql.save()
            
        return render(request, 'account/text.html', context={'text': '至信箱收取驗證信件'})
        # except :
            # print('mail error')
            # return render(request, 'account/register.html')

def register_verify(request):
    try:
        token = request.GET.get('key', 'default_value')
        result = RegisterVerify.objects.get(verify_token=token)
    
        time = result.token_expiration
    #print(time)
        userid = result.account_id.user_id
    #print('ok2')
        time = timezone.make_naive(time, timezone=dt_timezone.utc)
    #print('ok3')
        print(userid)
        if datetime.now() < time:  #檢查token是否到期
            
            result = Webusers.objects.get(user_id=userid)
            result.is_active = '1'
            result.save()
                       
            return render(request, 'account/register_verify.html')
        else:
            return render(request, 'account/text.html', context={'text':'此連結已失效'}) 
    except:
        return render(request, 'account/text.html', context={'text':'此連結已失效'}) 

def forget(request):
    if request.method == 'GET':
        return render(request, 'account/forgetpasswd.html', context={})
    elif request.method == 'POST':
        try:
            email = request.POST["sentEmail"]  #取得mail
            userid = Webusers.objects.get(email=email).user_id

            if userid:  #判斷是否有該帳號，若有
                reset_token = hashlib.sha256(str(uuid.uuid4()).encode('utf-8')).hexdigest()  #製作token

                current_time = datetime.now()  #取得當前時間
                new_time = current_time + timedelta(hours=8,minutes=10)  #增加10分鐘
                formatted_time = new_time.strftime("%Y-%m-%d %H:%M:%S")  #格式化時間

                PasswordResets(account_id_id=userid, token_expiration=formatted_time, reset_token=reset_token).save()

                mailcontent = f'請點選下方連結更改新密碼' + '\n' + f'http://travel.yiiii.org/account/resetpasswd/?key={reset_token}'
                send_mail('忘記密碼', mailcontent, "0988118277y@gmail.com", [email]) # django的發信def
                return render(request, 'account/text.html', context={'text':'請至信箱收取驗證信'})
            
        except:  #判斷是否有該帳號，若無
            return render(request, 'account/forgetpasswd.html', context={'status':'信箱輸入錯誤'})

def reset(request):
    if request.method == 'GET':
        try:
            token = request.GET.get('key', 'default_value')
            result = PasswordResets.objects.get(reset_token=token, was_used='0')
            userid = result.account_id.user_id
            time = result.token_expiration
            time = timezone.make_naive(time, timezone=dt_timezone.utc)
            
            if datetime.now() < time:  #檢查token是否到期
                return render(request, 'account/reset.html', context={'key':f'{token}'})
            else:
                return render(request, 'account/text.html', context={'text':'此連結已失效'}) 
        except:
            return render(request, 'account/text.html', context={'text':'此連結已失效'}) 
        
    elif request.method == 'POST':
        token = request.POST["token"]
        password = request.POST["password"]
        checkpassword = request.POST["checkpassword"]        
        if password == checkpassword:
            result = PasswordResets.objects.get(reset_token=token)
            userid = result.account_id.user_id
            result = Webusers.objects.get(user_id=userid)
            result.password = password
            result.save()
            result = PasswordResets.objects.get(reset_token=token)
            result.was_used = '1'
            result.save()
            return render(request, 'account/text.html', context={'text':'密碼更新完成'}) 
        else:
            return render(request, 'account/reset.html', context={'key':f'{token}','text':'密碼不一致'})    



def fix(request):
    if request.method == 'GET':
        if 'name' in request.session:
            return render(request, 'account/fix.html')
        else:
            return redirect("/account/login")
    elif request.method == 'POST':
        password = request.POST["password"]
        checkpassword = request.POST["checkpassword"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        username = request.POST["username"]

        account = request.session['name']
        result = Webusers.objects.get(account = account)
        if (password != "") and (checkpassword != ""):
            if password == checkpassword:
                result.password = password
                result.save()
        else:
            print("Password & checkPassword Must Key IN!")
        
        if email != "":
            result.email = email
            result.save()

        if username != "":
            result.username = username
            result.save()

        if phone != "":
            result.phone = phone
            result.save()

        return redirect('/')