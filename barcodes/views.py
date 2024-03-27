from django.shortcuts import render, redirect, HttpResponseRedirect
import aspose.barcode as barcode
import aspose.barcode.generation as barcode_generation
from barcodes.models import Barcodes, Stores
from account.models import Webusers
import random
from datetime import date
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.


@csrf_exempt
def unused(request):
    image_url = "barcode.png"
    if request.method == 'GET':
        if 'name' in request.session:
            account = request.session['name']
            user_id = Webusers.objects.get(account=account).user_id
            personal_barcode = Barcodes.objects.filter(user_id=user_id)
            today = date.today()
            # 未使用的條碼
            expired_barcodes = []
            for i in range(1, 6):
                expired_barcode = personal_barcode.filter(
                    used_status=0, used_end__gt=today, store_id=i)
                expired_barcodes.append(expired_barcode)
            df = pd.DataFrame(expired_barcodes)
            df_trans = df.T
            count = 0
            for i in df_trans.values:
                for j in i:
                    if j is None:
                        continue
                    else:
                        count += 1
            shop_all = Stores.objects.all()
            return render(request, 'unused.html', locals())
        else:
            return redirect("/account/login")
    elif request.method == 'POST':
        data = json.loads(request.body)
        image_url = data.get('imageUrl', '')
        print(image_url)
        bar_number = image_url.split("barcode/")[1].split(".jpg")[0]
        print(bar_number)
        bar = Barcodes.objects.get(barcode_number=bar_number)
        bar.used_status = "1"
        bar.save()
        return HttpResponseRedirect(request.path)


def delay(request):
    if request.method == 'GET':
        if 'name' in request.session:
            account = request.session['name']
            user_id = Webusers.objects.get(account=account).user_id
            personal_barcode = Barcodes.objects.filter(user_id=user_id)
            today = date.today()
            # 已過期的條碼
            expired_barcodes = []
            for i in range(1, 6):
                expired_barcode = personal_barcode.filter(
                    used_status=0, used_end__lt=today, store_id=i)
                expired_barcodes.append(expired_barcode)
            df = pd.DataFrame(expired_barcodes)
            df_trans = df.T
            count = 0
            for i in df_trans.values:
                for j in i:
                    if j is None:
                        continue
                    else:
                        count += 1
            shop_all = Stores.objects.all()
            return render(request, 'delay.html', locals())
        else:
            return redirect("/account/login")


def used(request):
    if request.method == 'GET':
        if 'name' in request.session:
            account = request.session['name']
            user_id = Webusers.objects.get(account=account).user_id
            personal_barcode = Barcodes.objects.filter(user_id=user_id)
            today = date.today()
            # 已使用的條碼
            expired_barcodes = []
            for i in range(1, 6):
                expired_barcode = personal_barcode.filter(
                    used_status=1, store_id=i)
                expired_barcodes.append(expired_barcode)
            df = pd.DataFrame(expired_barcodes)
            df_trans = df.T
            count = 0
            for i in df_trans.values:
                for j in i:
                    if j is None:
                        continue
                    else:
                        count += 1
            shop_all = Stores.objects.all()
            return render(request, 'used.html', locals())
        else:
            return redirect("/account/login")


# def produce(request):
#     # 暫定寫２
#     user_id = '2'

#     price = ["20", "40", "70", "120", "200"]
#     selected_price = random.choice(price)
#     store_id_all = Stores.objects.order_by('store_id')
#     random_store = random.choice(store_id_all)
#     # 亂數產生 10 碼數字
#     generated_number = "BC"+str(random.randint(0, 9999999999)).zfill(10)
#     existing_barcode = Barcodes.objects.filter(
#         barcode_number=generated_number).first()
#     if existing_barcode:
#         # 如果已存在相同的 barcode_number，重新生成
#         while existing_barcode:
#             generated_number = str(random.randint(0, 9999999999)).zfill(10)
#             existing_barcode = Barcodes.objects.filter(
#                 barcode_number=generated_number).first()

#     generator = barcode_generation.BarcodeGenerator(
#         barcode_generation.EncodeTypes.CODE_39_STANDARD)
#     # 代碼文本
#     generator.code_text = generated_number
#     # 保存生成的條碼
#     generator.save(f"static/barcode/{generated_number}.jpg")
#     # generator.save(f"static/img/barcode/{generated_number}已使用.jpg")
#     barcodes = Barcodes(
#         barcode_number=generated_number,
#         user_id=user_id,
#         store_id=random_store.store_id,
#         face_price=selected_price,
#         used_status="0",
#         barcode_img0=f"{generated_number}.jpg",
#         # barcode_img1=f"{generated_number}已使用.jpg"
#     )
#     barcodes.save()

    # return render(request, 'management/index.html', locals())
