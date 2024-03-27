from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from datetime import timedelta
from account.models import Webusers
from member_management.models import Points, PointHistory
from message.models import Messages
from RecommenderSystem.models import ShopsData
from barcodes.models import Barcodes, Stores
import random
from datetime import date
import pandas as pd
import aspose.barcode.generation as barcode_generation

# Create your views here.


def index(request):
    if request.method == 'GET':
        if 'name' in request.session:
            account = request.session['name']
            user_id = Webusers.objects.get(account=account).user_id
            point = Points.objects.get(user_id=user_id)
            message = Messages.objects.filter(user_id=user_id)

            # #補現有帳號的資料
            # users = Webusers.objects.filter(is_active=1)
            # for user in users:
            # sql = Points()
            # sql.user_id = user.user_id
            # sql.havepoint = 0
            # sql.todaypoint = 0
            # sql.save()

            return render(request, 'management/index.html', context={
                'havepoint': point.havepoint,
                'todaypoint': (5 - point.todaypoint),
                'message': len(message),
            })
        else:
            return redirect("/account/login")
    elif request.method == 'POST':
        account = request.session['name']
        user_id = Webusers.objects.get(account=account).user_id
        point = Points.objects.get(user_id=user_id)
        message = Messages.objects.filter(user_id=user_id)

        if point.havepoint >= 30:
            point.havepoint = Points.objects.get(
                user_id=user_id).havepoint - 30
            point.save()

            sql = PointHistory()
            sql.user_id = user_id
            sql.point = -30
            sql.content = '抽獎'
            sql.save()

            price = ["20", "40", "70", "120", "200"]
            selected_price = random.choice(price)
            store_id_all = Stores.objects.order_by('store_id')
            random_store = random.choice(store_id_all)
            # 亂數產生 10 碼數字
            generated_number = "BC" + \
                str(random.randint(0, 9999999999)).zfill(10)
            existing_barcode = Barcodes.objects.filter(
                barcode_number=generated_number).first()
            if existing_barcode:
                # 如果已存在相同的 barcode_number，重新生成
                while existing_barcode:
                    generated_number = str(
                        random.randint(0, 9999999999)).zfill(10)
                    existing_barcode = Barcodes.objects.filter(
                        barcode_number=generated_number).first()

            generator = barcode_generation.BarcodeGenerator(
                barcode_generation.EncodeTypes.CODE_39_STANDARD)
            # 代碼文本
            generator.code_text = generated_number
            # 保存生成的條碼
            generator.save(f"static/img/barcode/{generated_number}.jpg")
            # generator.save(f"static/barcode/{generated_number}已使用.jpg")
            barcodes = Barcodes(
                barcode_number=generated_number,
                user_id=user_id,
                store_id=random_store.store_id,
                face_price=selected_price,
                used_status="0",
                barcode_img0=f"{generated_number}.jpg",
                # barcode_img1=f"{generated_number}已使用.jpg"
            )
            barcodes.save()
            bar_queryset = Barcodes.objects.filter(
                barcode_number=generated_number)
            bar = bar_queryset.first()

        return render(request, 'management/index.html', context={
            'havepoint': point.havepoint,
            'todaypoint': (5 - point.todaypoint),
            'message': len(message),
            'bar': bar.barcode_img0 if bar else None,

        })


def message_detail(request):
    if request.method == 'GET':
        if 'name' in request.session:
            account = request.session['name']
            user_id = Webusers.objects.get(account=account).user_id
            messages = Messages.objects.filter(user_id=user_id)

            if messages:
                html = '''
                    <thead>
                    <tr>
                        <th scope="col">編號</th>
                        <th scope="col">店家</th>
                        <th scope="col">留言</th>
                        <th scope="col">時間</th>
                    </tr>
                    </thead>
                    <tbody>
                    '''
                for index, message in enumerate(messages):
                    html += f'''
                        <tr>
                            <td>{index + 1}</td>
                            <td>{ShopsData.objects.get(id=message.page).shopName}</td>
                            <td>{message.content}</td>
                            <td>{str(message.updated_at + timedelta(hours=8))[:19]}</td>
                        </tr>
                        '''
                html += '</tbody>'
            else:
                html = '<p class="nomessage">沒有有留言</p>'

            return render(request, 'management/message_details.html', context={'messages': mark_safe(html), 'total_message': len(messages)})
        else:
            return redirect("/account/login")


def point_detail(request):
    account = request.session['name']
    user_id = Webusers.objects.get(account=account).user_id
    points = PointHistory.objects.filter(user_id=user_id)
    pointinfo = Points.objects.get(user_id=user_id)

    if points:
        html = '''
            <thead>
            <tr>
                <th scope="col">編號</th>
                <th scope="col">點數</th>
                <th scope="col">說名</th>
                <th scope="col">時間</th>
            </tr>
            </thead>
            <tbody>
            '''
        for index, point in enumerate(points):
            html += f'''
                <tr>
                    <td>{index + 1}</td>
                    <td>{point.point}</td>
                    <td>{point.content}</td>
                    <td>{str(point.updated_at + timedelta(hours=8))[:19]}</td>
                </tr>
                '''
        html += '</tbody>'
    else:
        html = '<p class="nomessage">沒有點數紀錄</p>'

    return render(request, 'management/point_details.html', context={'messages': mark_safe(html), 'total_point': pointinfo.havepoint})
