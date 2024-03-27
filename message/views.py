from django.shortcuts import render, redirect
import re
from message.models import Messages,MessageReport
from account.models import Webusers
from member_management.models import Points,PointHistory
from django.core.mail import send_mail

# Create your views here.
def save_content(request):

    if request.method == 'POST':
        if 'name' in request.session:
            content = request.POST["message"].replace("'", "\\'")
            account = request.session['name']
            user = Webusers.objects.get(account=account).user_id
            referer_url = request.META.get('HTTP_REFERER')
            pattern = r'/(\d+)$'
            page = re.search(pattern, referer_url).group(1)
            sql = Messages()
            sql.user_id = user
            sql.content = content
            sql.page = page
            sql.save()
            
            if Points.objects.get(user_id=user).todaypoint < 5:
                sql = PointHistory()
                sql.user_id = user
                sql.point = 1
                sql.content = '每日留言獎勵'
                sql.save()
                
                sql = Points.objects.get(user_id=user)
                sql.havepoint = Points.objects.get(user_id=user).havepoint + 1
                sql.todaypoint = Points.objects.get(user_id=user).todaypoint + 1
                sql.save()
                
            return redirect(referer_url)
        else:
            return redirect("/account/login")
            

def messageReport(request):
    if request.method == 'POST':
        if 'name' in request.session:
            asktitle = request.POST["asktitle"]
            content = request.POST["message"]
            account = request.session['name']
            user = Webusers.objects.get(account=account)
            referer_url = request.META.get('HTTP_REFERER')
            
            sql = MessageReport()
            sql.user_id = user.user_id
            sql.title = asktitle
            sql.content = content
            sql.save()

            mailcontent = f'您的問題 " {content} " ，我們已經收到，稍後會有專人回覆您'
            send_mail(f'會員問題：{asktitle}', mailcontent, "0988118277y@gmail.com", [user.email]) 
            send_mail(f'會員問題：{asktitle}', f'會員ID:{user.user_id}有個問題，問題：{content}，請盡速處理', "0988:118277y@gmail.com", ['dspring1995@gmail.com'])
            
            return redirect(referer_url)

        else:
            return redirect("/account/login")
    else:
        return redirect("/account/login")
        