# -*- coding: utf-8 -*-
from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuArea, RichMenuSize, RichMenuBounds, PostbackAction, MessageAction
import requests

import settings

line_bot_api = LineBotApi(settings.access_token)

# #check rich menu
# richmenus=line_bot_api.get_rich_menu_list()
# print(richmenus)

# #set default rich menu
# url=f'https://api.line.me/v2/bot/user/all/richmenu/{non_id}'
# headers = {
#     'Authorization': 'Bearer ' + settings.access_token
# }
# res=requests.post(url, headers=headers)
# print(res)


# create richmenu
rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=843),
    selected=True,
    name="none_room",
    chat_bar_text="メニューを開く・閉じる",
    areas=[
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=0, width=1250, height=843),
            action=MessageAction(text='部屋を作る')),
        RichMenuArea(
            bounds=RichMenuBounds(x=1250, y=0, width=1250, height=843),
            action=MessageAction(text='部屋に入る'))
    ]
)
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

# upload image
with open('static/none_room.png', 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)

print(f'richmenu_id = "{rich_menu_id}"')

# create richmenu
rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=843),
    selected=True,
    name="with_room",
    chat_bar_text="メニューを開く・閉じる",
    areas=[
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=0, width=1250, height=843),
            action=MessageAction(text='退出する')),
        RichMenuArea(
            bounds=RichMenuBounds(x=1250, y=0, width=1250, height=843),
            action=MessageAction(text='ゲームを開始する'))
    ]
)
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

# upload image
with open('static/with_room.png', 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)

print(f'richmenu_id = "{rich_menu_id}"')

# create richmenu
rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=843),
    selected=True,
    name="wait",
    chat_bar_text="メニューを開く・閉じる",
    areas=[RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=1, height=1),
        action=MessageAction(text='none'))]
)
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

# upload image
with open('static/wait.png', 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)

print(f'richmenu_id = "{rich_menu_id}"')

# create richmenu
rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=843),
    selected=True,
    name="select",
    chat_bar_text="メニューを開く・閉じる",
    areas=[RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=1, height=1),
        action=MessageAction(text='none'))]
)
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

# upload image
with open('static/select.png', 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)

print(f'richmenu_id = "{rich_menu_id}"')

# create richmenu
for role in settings.roles.keys():
    if role in ['guest4', 'guest']:
        continue
    if role in ['spy', 'butler']:
        areas = [RichMenuArea(
            bounds=RichMenuBounds(x=0, y=0, width=834, height=843),
            action=MessageAction(text='効果を使う')),
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=843, width=2500, height=220),
                action=MessageAction(text='投票する'))]
    else:
        areas = [RichMenuArea(
            bounds=RichMenuBounds(x=0, y=0, width=1, height=1),
            action=MessageAction(text='none')),
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=843, width=2500, height=220),
                action=MessageAction(text='投票する'))]

    rich_menu_to_create = RichMenu(
        size=RichMenuSize(width=2500, height=1063),
        selected=True,
        name=role,
        chat_bar_text="メニューを開く・閉じる",
        areas=areas
    )
    rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

    # upload image
    with open(f'static/{role}.png', 'rb') as f:
        line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)

    print(f'{role} = "{rich_menu_id}"')
