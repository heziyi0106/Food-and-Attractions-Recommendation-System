from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import re
from message.models import Messages
from account.models import Webusers
from RecommenderSystem.models import ShopsData,  ShopsKeyWords  # 匯入model
from lineBot.models import LineAccountLink
from member_management.models import Points
from barcodes.models import Barcodes, Stores
from django.db.models import Q
import requests
import random
# 加入line message的套件
from linebot import LineBotApi,  WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, FlexSendMessage, ImageSendMessage, BubbleContainer, BoxComponent, TextComponent, ButtonComponent, PostbackAction, PostbackEvent

# 帶入對應的token,secret
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parse = WebhookParser(settings.LINE_CHANNEL_SECRET)
# Create your views here.


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        # 驗證
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        # line的內容解析編碼
        body = request.body.decode('utf-8')
        # 驗證
        try:
            events = parse.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        # 解析
        for event in events:
            # 如果是文字類的(MessageEvant)
            if isinstance(event, MessageEvent):
                all_values = ShopsData.objects.order_by("id")
                random_five_bothvalues = random.sample(list(all_values), 5)
                eat_values = ShopsData.objects.filter(shopType=0)
                random_five_eatsvalues = random.sample(list(eat_values), 5)
                place_values = ShopsData.objects.filter(shopType=1)
                random_five_placesvalues = random.sample(list(place_values), 5)
                if '查詢點數' == event.message.text:
                    if LineAccountLink.objects.filter(lineid=event.source.user_id).exists():
                        user_id = LineAccountLink.objects.get(
                            lineid=event.source.user_id).user_id
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(
                            text=f"目前還有 {point_check(user_id)} 點"))
                    else:
                        flex_message = FlexSendMessage(
                            alt_text="尚未綁定帳號",
                            contents=BubbleContainer(
                                body=BoxComponent(
                                    layout="vertical",
                                    contents=[TextComponent(
                                        text="尚未綁定帳號", weight="bold", size="md", align="center")]
                                ),
                                footer=BoxComponent(
                                    layout="vertical",
                                    contents=[ButtonComponent(
                                        style="primary", action=PostbackAction(label="綁定帳號", data="Link"))]
                                )
                            )
                        )
                        line_bot_api.reply_message(
                            event.reply_token, flex_message)
                elif '查詢折價券' == event.message.text:
                    if LineAccountLink.objects.filter(lineid=event.source.user_id).exists():
                        user_id = LineAccountLink.objects.get(
                            lineid=event.source.user_id).user_id
                        barcodes = barcode_check(user_id)
                        if barcodes:
                            flex_message = FlexSendMessage(
                                alt_text="折價券一覽",
                                contents=BubbleContainer(
                                    body=BoxComponent(
                                        layout="vertical",
                                        contents=[TextComponent(
                                            text="折價券一覽", weight="bold", size="md", align="center")]
                                    ),
                                    footer=BoxComponent(
                                        layout="vertical",
                                        contents=[item for i, barcode in enumerate(barcodes) for item in [
                                            ButtonComponent(
                                                style="primary",
                                                action=PostbackAction(
                                                    label=f"第{i+1}個折價券，{Stores.objects.get(store_id=barcode.store_id).store_name}的{barcode.face_price}元",
                                                    data=f"barcodenum={barcode.barcode_number}"
                                                )
                                            ),
                                            BoxComponent(
                                                layout="vertical", height="20px"),
                                        ]
                                        ]
                                    )
                                )
                            )
                            line_bot_api.reply_message(
                                event.reply_token, flex_message)
                        else:
                            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                                text=f"目前還未有折價券，可以透過留言累積點數，抽取折價券"))
                    else:
                        flex_message = FlexSendMessage(
                            alt_text="尚未綁定帳號",
                            contents=BubbleContainer(
                                body=BoxComponent(
                                    layout="vertical",
                                    contents=[TextComponent(
                                        text="尚未綁定帳號", weight="bold", size="md", align="center")]
                                ),
                                footer=BoxComponent(
                                    layout="vertical",
                                    contents=[ButtonComponent(
                                        style="primary", action=PostbackAction(label="綁定帳號", data="Link"))]
                                )
                            )
                        )
                        line_bot_api.reply_message(
                            event.reply_token, flex_message)
                elif '帳號連接' == event.message.text:
                    if LineAccountLink.objects.filter(lineid=event.source.user_id).exists():
                        flex_message = FlexSendMessage(
                            alt_text="已有帳號綁定",
                            contents=BubbleContainer(
                                body=BoxComponent(
                                    layout="vertical",
                                    contents=[TextComponent(
                                        text="已有帳號綁定", weight="bold", size="md", align="center")]
                                ),
                                footer=BoxComponent(
                                    layout="vertical",
                                    contents=[ButtonComponent(
                                        style="primary", action=PostbackAction(label="解除綁定帳號", data="unLink"))]
                                )
                            )
                        )
                        line_bot_api.reply_message(
                            event.reply_token, flex_message)
                    else:
                        flex_message = FlexSendMessage(
                            alt_text="尚未綁定帳號",
                            contents=BubbleContainer(
                                body=BoxComponent(
                                    layout="vertical",
                                    contents=[
                                        TextComponent(
                                            text="尚未綁定帳號", weight="bold", size="md", align="center")
                                    ]
                                ),
                                footer=BoxComponent(
                                    layout="vertical",
                                    contents=[
                                        ButtonComponent(style="primary", action=PostbackAction(
                                            label="綁定帳號", data="Link"))
                                    ]
                                )
                            )
                        )
                        line_bot_api.reply_message(
                            event.reply_token, flex_message)
                elif '隨便' in event.message.text:
                    messages = []
                    for i, shop in enumerate(random_five_bothvalues):

                        messages.append(
                            TextSendMessage(
                                text=f"{i+1}\n{shop.shopName}\nhttps://www.google.com/maps/search/{shop.shopName}"
                            )
                        )
                    line_bot_api.reply_message(
                        event.reply_token,
                        messages  # 一次性回复所有消息
                    )

                elif '好吃' in event.message.text or '美食' in event.message.text:
                    messages = []
                    for i, shop in enumerate(random_five_eatsvalues):

                        messages.append(
                            TextSendMessage(
                                text=f"{i+1}\n{shop.shopName}\nhttps://www.google.com/maps/search/{shop.shopName}"
                            )
                        )

                    line_bot_api.reply_message(
                        event.reply_token,
                        messages  # 一次性回复所有消息
                    )

                elif '好玩' in event.message.text or '景點' in event.message.text:
                    messages = []
                    for i, shop in enumerate(random_five_placesvalues):
                        messages.append(
                            TextSendMessage(
                                text=f"{i+1}\n{shop.shopName}\nhttps://www.google.com/maps/search/{shop.shopName}"
                            )
                        )
                    line_bot_api.reply_message(
                        event.reply_token,
                        messages  # 一次性回复所有消息
                    )

                # 直接用店名、地址找相似
                elif ShopsData.objects.filter(Q(shopName__icontains=event.message.text) | Q(shopAddress__icontains=event.message.text)).exists():
                    try:
                        matching_shops = ShopsData.objects.filter(
                            shopName__icontains=event.message.text)
                        if matching_shops:
                            messages = []
                            count = 0
                            for shopdata in matching_shops:
                                similar_data = ShopsKeyWords.objects.get(
                                    shop_id=shopdata.id)
                                similar_shop_ids = similar_data.similarityShop
                                similar_shop_ids_list = [
                                    num for num in similar_shop_ids.strip('[]').split(',')]
                                # print(similar_shop_ids)
                                for i, shop_id in enumerate(similar_shop_ids_list):
                                    similar_shop = ShopsData.objects.get(
                                        id=shop_id)
                                    if similar_shop:
                                        messages.append(
                                            TextSendMessage(
                                                text=f"{i+1}\n{similar_shop.shopName}\nhttps://www.google.com/maps/search/{similar_shop.shopName}"
                                            )
                                        )
                                        count += 1
                                        if count > 5:
                                            break
                        else:
                            matching_shops = ShopsData.objects.filter(
                                shopAddress__icontains=event.message.text)
                            messages = []
                            count = 0
                            for i, shopdata in enumerate(matching_shops):
                                messages.append(
                                    TextSendMessage(
                                        text=f"{i+1}\n{shopdata.shopName}\nhttps://www.google.com/maps/search/{shopdata.shopName}"
                                    )
                                )
                                count += 1
                                if count == 5:
                                    break
                        if len(messages) > 5:
                            messages = messages[:5]
                        line_bot_api.reply_message(
                            event.reply_token,
                            messages  # 一次性回复所有消息
                        )
                    except Exception as e:
                        print(e)
                    finally:
                        line_bot_api.reply_message(
                            event.reply_token,
                            # TextSendMessage(text='hello world')
                            # 鸚鵡機器人，原封不動還給使用者
                            TextSendMessage(text=f"沒有找到相似的！抱歉！")
                        )

                # 如果用店名跟地址找不到相似，用模糊搜尋
                elif not ShopsData.objects.filter(Q(shopName__icontains=event.message.text) | Q(shopAddress__icontains=event.message.text)).exists():
                    try:
                        matching_shops = ShopsKeyWords.objects.filter(
                            contentGroup__icontains=event.message.text)
                        if matching_shops:
                            messages = []
                            count = 0
                            random_shop = random.choice(matching_shops)
                            similar_shop_ids = random_shop.similarityShop
                            similar_shop_ids_list = [
                                num for num in similar_shop_ids.strip('[]').split(',')]
                            for i, shop in enumerate(similar_shop_ids_list):
                                similar_shop = ShopsData.objects.get(
                                    id=shop)
                                if similar_shop:
                                    messages.append(
                                        TextSendMessage(
                                            text=f"{i+1}\n{similar_shop.shopName}\nhttps://www.google.com/maps/search/{similar_shop.shopName}"
                                        )
                                    )
                                    count += 1
                                    if count >= 5:
                                        break

                        if len(messages) > 5:
                            messages = messages[:5]
                        line_bot_api.reply_message(
                            event.reply_token,
                            messages  # 一次性回复所有消息
                        )
                    except Exception as e:
                        print(e)
                    finally:
                        line_bot_api.reply_message(
                            event.reply_token,
                            # TextSendMessage(text='hello world')
                            # 鸚鵡機器人，原封不動還給使用者
                            TextSendMessage(text=f"沒有找到相似的！抱歉！")
                        )

                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        # TextSendMessage(text='hello world')
                        # 鸚鵡機器人，原封不動還給使用者
                        TextSendMessage(text=f"沒有找到相似的！抱歉！")
                    )

            elif isinstance(event, PostbackEvent):
                print(event.postback.data)
                if event.postback.data == "Link":
                    token = get_link_token(
                        event.source.user_id, settings.LINE_CHANNEL_ACCESS_TOKEN)
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(
                        text=f"https://travel.yiiii.org/account/login/?&linkToken={token}"))
                elif event.postback.data == "unLink":
                    sql = LineAccountLink.objects.get(
                        lineid=event.source.user_id)
                    # sql = LineAccountLink.objects.filter(user_id=2)
                    sql.delete()
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=f"已取消綁定"))
                elif 'barcodenum' in event.postback.data:
                    pattern = r'barcodenum=([A-Za-z0-9]+)'
                    num = re.search(pattern, event.postback.data).group(1)
                    img_url = r'https://travel.yiiii.org/static/img/barcode/' + \
                        Barcodes.objects.get(barcode_number=num).barcode_img0
                    print(img_url)
                    line_bot_api.reply_message(event.reply_token, ImageSendMessage(
                        original_content_url=img_url, preview_image_url=img_url))
            elif 'accountLink' == event.type:
                print(event.link.result)
                if 'ok' == event.link.result:
                    sql = LineAccountLink.objects.get(nonce=event.link.nonce)
                    sql.lineid = event.source.user_id
                    sql.save()
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"帳號綁定成功"))
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"帳號綁定失敗"))     
        return HttpResponse()
    else:
        return HttpResponseBadRequest()


def get_link_token(user_id, channel_access_token):
    url = f"https://api.line.me/v2/bot/user/{user_id}/linkToken"
    headers = {
        "Authorization": f"Bearer {channel_access_token}"
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('linkToken')
    else:
        print(f"Error: {response.status_code}")
        return None


def point_check(user_id):
    return (Points.objects.get(user_id=user_id).havepoint)


def barcode_check(user_id):
    try:
        return (Barcodes.objects.filter(user_id=user_id).filter(used_status=0))
    except:
        return (None)
