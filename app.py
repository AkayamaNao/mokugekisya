# # -*- coding: utf-8 -*-
from flask import request, abort, Flask
from sqlalchemy import create_engine, func
import pandas as pd
from sqlalchemy.orm import sessionmaker
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, PostbackEvent
import requests
import json
import random, string
import ast
import uuid
import numpy as np

import settings
from models import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
db_engine = create_engine(settings.db_info, pool_pre_ping=True)
line_bot_api = LineBotApi(settings.access_token)
handler = WebhookHandler(settings.secret_key)
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + settings.access_token
}
reply_url = 'https://api.line.me/v2/bot/message/reply'
push_url = 'https://api.line.me/v2/bot/message/multicast'

with app.app_context():
    db.init_app(app)
    # db.drop_all()  # Remove on release
    db.create_all()


def gene_id(s):
    while True:
        id = '@' + ''.join([random.choice(string.ascii_lowercase) for i in range(4)])
        user = s.query(Users).filter_by(room_id=id).first()
        if user is None:
            return id


def push_message(users, messages):
    # users = ['U7f877a02271b4fbfcfa8d4c3a33c1290']
    data = {'to': users, 'messages': messages}
    res = requests.post(push_url, data=json.dumps(data), headers=headers)
    return res


def select_role(number, game_id):
    query = f'''
        select roles.user_id,users.name,roles.number,roles.role,roles.vote,roles.ability from users
        right outer join (select * from roles where game_id = '{game_id}' and status = 1) as roles on users.id = roles.user_id;
        '''
    df = pd.read_sql(query, db_engine)
    remain_role = df[df['number'] == 0]['role'].to_list()[0]
    try:
        my_role = df[df['number'] == number]['role'].to_list()[0]
    except:
        push_message(df[df['number'] > 0]['user_id'].to_list(), [{
            "type": "text",
            "text": '話し合いを開始してください（約3分）\n話し合いが終了したら投票をしてください'
        }])
        for index, row in df[df['number'] > 0].iterrows():
            try:
                line_bot_api.link_rich_menu_to_user(row['user_id'], settings.roles[row['role']]["richmenu"])
            except:
                pass
        return 0
    try:
        line_bot_api.link_rich_menu_to_user(df[df['number'] == number]['user_id'].to_list()[0], settings.select_id)
    except:
        pass

    try:
        next_user_name = df[df['number'] == number + 1]['name'].to_list()[0]
    except:
        next_user_name = '客間'

    text = ''
    if number > 1:
        prev_user_name = df[df['number'] == number - 1]['name'].to_list()[0]
        text += f'{prev_user_name} から {settings.roles[remain_role]["name"]} が送られてきました\n\n'
    text += f'どちらの役を {next_user_name} に送りますか？'

    items = [{
        "type": "action",
        "action": {
            "type": "postback",
            "label": f'{settings.roles[remain_role]["name"]}',
            "text": f'{settings.roles[remain_role]["name"]} を {next_user_name} に送る',
            "data": "{'action':'role_select', 'role':'" + remain_role + "'}"
        }
    }, {
        "type": "action",
        "action": {
            "type": "postback",
            "label": f'{settings.roles[my_role]["name"]}',
            "text": f'{settings.roles[my_role]["name"]} を {next_user_name} に送る',
            "data": "{'action':'role_select', 'role':'" + my_role + "'}"
        }
    }]
    push_message([df[df['number'] == number]['user_id'].to_list()[0]], [{
        "type": "text",
        "text": text,
        "quickReply": {
            "items": items
        }
    }])


@app.route('/')
def index():
    return 'hello, world'


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    user_name = profile.display_name
    text = event.message.text

    Session = sessionmaker(bind=db_engine)
    s = Session()
    user = s.query(Users).filter_by(id=user_id).first()
    if user:
        room_id = user.room_id
        user.name = user_name
    else:
        user = Users(id=user_id, name=user_name)
        s.add(user)
        s.commit()
        try:
            line_bot_api.link_rich_menu_to_user(user_id, settings.none_room_id)
        except:
            pass
        room_id = None

    reply_json = []
    if text == '部屋を作る':
        my_role = s.query(Roles).filter_by(user_id=user_id, status=1).first()
        if my_role:
            reply_json.append({
                "type": "text",
                "text": '現在、ゲーム進行中です'
            })
        else:
            room_id = gene_id(s)
            user.room_id = room_id
            s.commit()
            reply_json.append({
                "type": "text",
                "text": "新しい部屋を作りました。\n一緒に遊ぶ友達に下記の部屋IDを教えてゲームを始めよう！"
            })
            reply_json.append({
                "type": "text",
                "text": room_id
            })
            try:
                line_bot_api.link_rich_menu_to_user(user_id, settings.with_room_id)
            except:
                pass
    elif text == '部屋に入る':
        my_role = s.query(Roles).filter_by(user_id=user_id, status=1).first()
        if my_role:
            reply_json.append({
                "type": "text",
                "text": '現在、ゲーム進行中です'
            })
        else:
            reply_json.append({
                "type": "text",
                "text": "一緒に遊ぶ友達に部屋IDを教えてもらってこのトークルームに部屋IDを送信するとその部屋に入ることができます。"
            })
    elif text == '退出する':
        user.room_id = None
        reply_json.append({
            "type": "text",
            "text": "退出しました。"
        })
        my_role = s.query(Roles).filter_by(user_id=user_id, status=1).first()
        if my_role:
            roles = s.query(Roles).filter_by(game_id=my_role.game_id).all()
            for role in roles:
                role.status = 0
                if role.number > 0:
                    try:
                        line_bot_api.link_rich_menu_to_user(role.user_id, settings.with_room_id)
                    except:
                        pass
        try:
            line_bot_api.link_rich_menu_to_user(user_id, settings.none_room_id)
        except:
            pass
        s.commit()
    elif text == 'ゲームを開始する':
        my_role = s.query(Roles).filter_by(user_id=user_id, status=1).first()
        if room_id is None:
            reply_json.append({
                "type": "text",
                "text": '部屋に入ってください'
            })
        elif my_role:
            reply_json.append({
                "type": "text",
                "text": '現在、ゲーム進行中です'
            })
        else:
            query = f"select name from users where room_id='{room_id}';"
            df = pd.read_sql(query, db_engine)
            num = len(df)
            text = f'このゲームは3~6人用です\n現在この部屋には{num}人います'
            items = []
            if num in settings.numbers_levels.keys():
                text = 'どのレベルで遊びますか？\n'
                for i in settings.numbers_levels[num]:
                    text += f'\nレベル{i + 1}   '
                    level = settings.levels[i]
                    text += ','.join([settings.roles[role]['name'] for role in level['roles']])
                    text += f'×{num + level["plus"] - len(level["roles"]) + 1}'
                    text += f'  {level["rule"]}'
                    items.append({
                        "type": "action",
                        "action": {
                            "type": "postback",
                            "label": f'レベル{i + 1}',
                            "text": f'レベル{i + 1}',
                            "data": "{'action':'level_select', 'level':'" + str(i) + "'}"
                        }
                    })
            items.append({
                "type": "action",
                "action": {
                    "type": "postback",
                    "label": 'キャンセル',
                    "text": 'キャンセル',
                    "data": "{'action':'none'}"
                }
            })
            reply_json.append({
                "type": "text",
                "text": text,
                "quickReply": {
                    "items": items
                }
            })
    elif text == '効果を使う':
        my_role = s.query(Roles).filter_by(user_id=user_id, status=1).first()
        if my_role is None:
            reply_json.append({
                "type": "text",
                "text": "現在、効果を使えません"
            })
        elif my_role.role in ['spy', 'butler'] and my_role.ability == 0:
            items = [{
                "type": "action",
                "action": {
                    "type": "postback",
                    "label": 'はい',
                    "text": 'はい',
                    "data": "{'action':'use_ability'}"
                }
            }, {
                "type": "action",
                "action": {
                    "type": "postback",
                    "label": 'いいえ',
                    "text": 'いいえ',
                    "data": "{'action':'none'}"
                }
            }]
            reply_json.append({
                "type": "text",
                "text": "効果を使いますか？",
                "quickReply": {
                    "items": items
                }
            })
        else:
            reply_json.append({
                "type": "text",
                "text": "現在、効果を使えません"
            })
    elif text == '投票する':
        my_role = s.query(Roles).filter_by(user_id=user_id, status=1).first()
        if my_role:
            if my_role.ability == 1:
                reply_json.append({
                    "type": "text",
                    "text": "あなたは投票権がありません"
                })
            elif my_role.vote is not None:
                reply_json.append({
                    "type": "text",
                    "text": "投票済みです"
                })
            else:
                query = f'''
                    select roles.user_id,users.name,roles.number,roles.role,roles.vote,roles.ability from users
                    right outer join (select * from roles where game_id = '{my_role.game_id}' and status = 1 and number > 0 and ability = 0) as roles on users.id = roles.user_id;
                    '''
                df = pd.read_sql(query, db_engine)
                items = []
                for index, row in df[df['number'] != my_role.number].sort_values('number').iterrows():
                    items.append({
                        "type": "action",
                        "action": {
                            "type": "postback",
                            "label": f'{row["name"]}',
                            "text": f'{row["name"]} さんに投票しました',
                            "data": "{'action':'vote', 'vote':'" + row["user_id"] + "'}"
                        }
                    })
                items.append({
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": f'客間',
                        "text": f'客間の人物に投票しました',
                        "data": "{'action':'vote', 'vote':'remain'}"
                    }
                })
                reply_json.append({
                    "type": "text",
                    "text": "誰をボイラー室行きにしますか？",
                    "quickReply": {
                        "items": items
                    }
                })
        else:
            reply_json.append({
                "type": "text",
                "text": "その操作は無効です"
            })
    elif text[0] == '@':
        my_role = s.query(Roles).filter_by(user_id=user_id, status=1).first()
        room_user = s.query(Users).filter_by(room_id=text).first()
        if my_role:
            reply_json.append({
                "type": "text",
                "text": "現在、ゲーム進行中です"
            })
        elif room_user:
            user.room_id = text
            s.commit()
            query = f"select name from users where room_id='{text}';"
            df = pd.read_sql(query, db_engine)
            member = '\n'.join(df['name'].to_list())
            reply_json.append({
                "type": "text",
                "text": f"部屋に入りました。現在この部屋には\n\n{member}\n\nがいます。"
            })
            try:
                line_bot_api.link_rich_menu_to_user(user_id, settings.with_room_id)
            except:
                pass
        else:
            reply_json.append({
                "type": "text",
                "text": f"部屋IDが違います。"
            })

    data = {'replyToken': event.reply_token, 'messages': reply_json}
    res = requests.post(reply_url, data=json.dumps(data), headers=headers)


@handler.add(PostbackEvent)
def postback(event):
    user_id = event.source.user_id
    data = event.postback.data
    data_dic = ast.literal_eval(data)

    Session = sessionmaker(bind=db_engine)
    s = Session()
    user = s.query(Users).filter_by(id=user_id).first()
    if user:
        room_id = user.room_id
    else:
        return 0

    reply_json = []
    if data_dic['action'] == 'level_select':
        level = int(data_dic['level'])
        query = f"select id,name from users where room_id='{room_id}';"
        df = pd.read_sql(query, db_engine)
        df = df.sample(frac=1)
        df = df.reset_index(drop=True)
        num = len(df)
        if num in settings.numbers_levels.keys():
            if level in settings.numbers_levels[num]:

                game_id = str(uuid.uuid4())
                level_roles = settings.levels[level]['roles']
                guest_num = num + settings.levels[level]["plus"] - len(level_roles) + 1
                guests = list(np.random.choice(['guest1', 'guest2', 'guest3', 'guest4'], guest_num, replace=False))
                roles = level_roles.copy()
                roles.remove('guest')
                roles = roles + guests

                if level >= 6:
                    roles.remove('murder')
                    role = list(np.random.choice(roles, 1))[0]
                    roles.remove(role)
                    s.add(Roles(game_id=game_id, number=-1, user_id='hidden', role=role))
                    role = list(np.random.choice(roles, 1))[0]
                    roles.remove(role)
                    s.add(Roles(game_id=game_id, number=-2, user_id='hidden', role=role))
                    roles.append('murder')
                if level == 7:
                    roles.remove('murder')
                    role = list(np.random.choice(roles, 1))[0]
                    roles.remove(role)
                    s.add(Roles(game_id=game_id, number=-3, user_id='invalid', role=role))
                    role = list(np.random.choice(roles, 1))[0]
                    roles.remove(role)
                    s.add(Roles(game_id=game_id, number=-4, user_id='invalid', role=role))
                    roles.append('murder')
                for index, row in df.iterrows():
                    role = list(np.random.choice(roles, 1))[0]
                    roles.remove(role)
                    s.add(Roles(game_id=game_id, number=index + 1, user_id=row['id'], role=role))
                    try:
                        if index == 0:
                            line_bot_api.link_rich_menu_to_user(row['id'], settings.select_id)
                        else:
                            line_bot_api.link_rich_menu_to_user(row['id'], settings.wait_id)
                    except:
                        pass
                s.add(Roles(game_id=game_id, number=0, user_id='remain', role=roles[0]))
                s.commit()

                text = ''
                text += ','.join([settings.roles[role]['name'] for role in level_roles])
                text += f'×{guest_num}'
                text += f'  {settings.levels[level]["rule"]}'
                members = '\n'.join(df['name'])

                push_message(df['id'].to_list(), [{
                    "type": "text",
                    "text": f"レベル{level + 1}でゲームスタート！\n\n<順番>\n{members}\n\n<役>\n{text}"
                }])

                select_role(1, game_id)
            else:
                reply_json.append({
                    "type": "text",
                    "text": f"{num}人でレベル{int(data_dic['level']) + 1}では遊べません"
                })
        else:
            reply_json.append({
                "type": "text",
                "text": f'このゲームは3~6人用です\n現在この部屋には{num}人います'
            })
    elif data_dic['action'] == 'role_select':
        role = data_dic['role']
        my_role = s.query(Roles).filter_by(user_id=user_id, status=1).first()
        remain_role = s.query(Roles).filter_by(number=0, status=1).first()
        if my_role.role == role:
            my_role.role = remain_role.role
            remain_role.role = role
            s.commit()
        try:
            line_bot_api.link_rich_menu_to_user(user_id, settings.wait_id)
        except:
            pass
        select_role(my_role.number + 1, my_role.game_id)
    elif data_dic['action'] == 'use_ability':
        my_role = s.query(Roles).filter_by(user_id=user_id, status=1).first()
        my_role.ability = 1
        s.commit()
        if my_role.role == 'spy':
            query = f'''
                select roles.user_id,users.name,roles.number,roles.role,roles.vote,roles.ability from users
                right outer join (select * from roles where game_id = '{my_role.game_id}' and status = 1 and number > 0 and ability = 0) as roles on users.id = roles.user_id;
                '''
            df = pd.read_sql(query, db_engine)
            items = []
            for index, row in df[df['number'] != my_role.number].sort_values('number').iterrows():
                items.append({
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": f'{row["name"]}',
                        "text": f'{row["name"]} さんをボイラー室行きにしました',
                        "data": "{'action':'spy_vote', 'vote':'" + row["user_id"] + "'}"
                    }
                })
            items.append({
                "type": "action",
                "action": {
                    "type": "postback",
                    "label": f'客間',
                    "text": f'客間の人物をボイラー室行きにしました',
                    "data": "{'action':'spy_vote', 'vote':'remain'}"
                }
            })
            reply_json.append({
                "type": "text",
                "text": "誰をボイラー室行きにしますか？",
                "quickReply": {
                    "items": items
                }
            })
        elif my_role.role == 'butler':
            query = f'''
                select * from roles where game_id = '{my_role.game_id}' and status = 1;
                '''
            df = pd.read_sql(query, db_engine)
            hidden_list = [df[df['number'] == -1]['role'].item(), df[df['number'] == -2]['role'].item()]
            hidden_list = [settings.roles[role]['name'] for role in hidden_list]

            reply_json.append({
                "type": "text",
                "text": f'伏せた2枚のカードは、 {" と ".join(hidden_list)} です'
            })
            reply_json.append({
                "type": "text",
                "text": f'{user.name} さんが 執事 の効果を使い、伏せた2枚のカードを確認しました。\n{user.name} さんは投票権を失いました。'
            })

            df = df[df['number'] > 0]
            df = df[df['number'] != my_role.number]
            push_message(df['user_id'].to_list(), [{
                "type": "text",
                "text": f'{user.name} さんが 執事 の効果を使い、伏せた2枚のカードを確認しました。\n{user.name} さんは投票権を失いました。'
            }])
        else:
            reply_json.append({
                "type": "text",
                "text": f'現在、効果を使えません'
            })
    elif data_dic['action'] == 'spy_vote':
        vote = data_dic['vote']
        my_role = s.query(Roles).filter_by(user_id=user_id, status=1).first()
        query = f'''
            select roles.user_id,users.name,roles.number,roles.role,roles.vote,roles.ability from users
            right outer join (select * from roles where game_id = '{my_role.game_id}' and status = 1) as roles on users.id = roles.user_id;
            '''
        df = pd.read_sql(query, db_engine)
        target = df[df['user_id'] == vote]

        if vote == 'remain':
            text = f'{user.name} さんが 探偵 の効果を使い、客間の人物 をボイラー室行きにしました\n\n'
        else:
            text = f'{user.name} さんが 探偵 の効果を使い、{target["name"].item()} さんをボイラー室行きにしました\n\n'

        if target['role'].item() == 'murder':
            wins = ['lawyer', 'rich', 'spy', 'butler', 'guest1', 'guest2', 'guest3', 'guest4']
        elif target['role'].item() == 'bomb':
            wins = ['bomb']
        else:
            wins = ['murder', 'partner']
        df.loc[df['number'] < 0, 'name'] = '伏せたカード'
        df.loc[df['number'] < -2, 'name'] = '除外したカード'
        df.loc[df['number'] == 0, 'name'] = '客間'
        text += '<<結果発表>>'
        for index, row in df.sort_values('number').iterrows():
            text += f'\n{row["name"]}   {settings.roles[row["role"]]["name"]}'
            if row['number'] > 0 and row["role"] in wins:
                text += '   ☆'
        df = df[df['number'] > 0]
        push_message(df['user_id'].to_list(), [{
            "type": "text",
            "text": text
        }])
        roles = s.query(Roles).filter_by(game_id=my_role.game_id).all()
        for role in roles:
            role.status = 0
        s.commit()
        for index, row in df[df['number'] > 0].iterrows():
            try:
                line_bot_api.link_rich_menu_to_user(row['user_id'], settings.with_room_id)
            except:
                pass
    elif data_dic['action'] == 'lawyer_vote':
        vote = data_dic['vote']
        my_role = s.query(Roles).filter_by(user_id=user_id, status=1).first()
        query = f'''
            select roles.user_id,users.name,roles.number,roles.role,roles.vote,roles.ability from users
            right outer join (select * from roles where game_id = '{my_role.game_id}' and status = 1) as roles on users.id = roles.user_id;
            '''
        df = pd.read_sql(query, db_engine)
        vote_df = df[df['number'] > 0]
        df.loc[df['number'] < 0, 'name'] = '伏せたカード'
        df.loc[df['number'] < -2, 'name'] = '除外したカード'
        df.loc[df['number'] == 0, 'name'] = '客間'
        text = '<<投票結果>>'
        for index, row in vote_df.sort_values('number').iterrows():
            if row["vote"] is None:
                text += f'\n{row["name"]}  → 投票なし'
            elif row["user_id"] == vote:
                text += f'\n{row["name"]}  → {df[df["user_id"] == row["vote"]]["name"].item()}(無効化)'
            elif row['role'] == 'rich':
                text += f'\n{row["name"]}  → {df[df["user_id"] == row["vote"]]["name"].item()}×２'
            else:
                text += f'\n{row["name"]}  → {df[df["user_id"] == row["vote"]]["name"].item()}'
        vote_df.loc[vote_df['user_id'] == vote, 'vote'] = None

        vote_count = vote_df['vote'].value_counts()
        rich = vote_df[vote_df['role'] == 'rich']
        if len(rich) == 1:
            vote_count[rich['vote'].item()] += 1
        target = vote_count[vote_count == vote_count.max()].index.to_list()
        target = [df[df['user_id'] == t]['role'].item() for t in target]
        if 'murder' in target:
            wins = ['lawyer', 'rich', 'spy', 'butler', 'guest1', 'guest2', 'guest3', 'guest4']
        else:
            wins = ['murder', 'partner']
        if 'bomb' in target:
            wins = ['bomb']

        text += '\n\n<<結果発表>>'
        for index, row in df.sort_values('number').iterrows():
            text += f'\n{row["name"]}   {settings.roles[row["role"]]["name"]}'
            if row['number'] > 0 and row["role"] in wins:
                text += '   ☆'
        push_message(vote_df['user_id'].to_list(), [{
            "type": "text",
            "text": text
        }])
        roles = s.query(Roles).filter_by(game_id=my_role.game_id).all()
        for role in roles:
            role.status = 0
        s.commit()
        for index, row in df[df['number'] > 0].iterrows():
            try:
                line_bot_api.link_rich_menu_to_user(row['user_id'], settings.with_room_id)
            except:
                pass

    elif data_dic['action'] == 'vote':
        vote = data_dic['vote']
        my_role = s.query(Roles).filter_by(user_id=user_id, status=1).first()
        my_role.vote = vote
        s.commit()
        try:
            line_bot_api.link_rich_menu_to_user(user_id, settings.wait_id)
        except:
            pass

        query = f'''
            select roles.user_id,users.name,roles.number,roles.role,roles.vote,roles.ability from users
            right outer join (select * from roles where game_id = '{my_role.game_id}' and status = 1) as roles on users.id = roles.user_id;
            '''
        df = pd.read_sql(query, db_engine)
        vote_df = df[df['number'] > 0]
        vote_df['text'] = '投票待ち'
        vote_df.loc[~vote_df['vote'].isna(), 'text'] = '投票済'
        vote_df.loc[vote_df['ability'] == 1, 'text'] = '投票権なし'
        if sum(vote_df['text'] == '投票待ち') > 0:
            text = '<<投票受付中>>'
            for index, row in vote_df.sort_values('number').iterrows():
                text += f'\n{row["name"]}   {row["text"]}'
            reply_json.append({
                "type": "text",
                "text": text
            })
        else:
            df.loc[df['number'] < 0, 'name'] = '伏せたカード'
            df.loc[df['number'] < -2, 'name'] = '除外したカード'
            df.loc[df['number'] == 0, 'name'] = '客間'
            lawyer = df[(df[['role', 'ability']] == ['lawyer', 0]).all(axis=1)]
            if len(lawyer) == 1:
                text = '<<投票結果>>'
                vote_list = []
                for index, row in vote_df.sort_values('number').iterrows():
                    if row["vote"] is None:
                        text += f'\n{row["name"]}  → 投票なし'
                    else:
                        text += f'\n{row["name"]}  → {df[df["user_id"] == row["vote"]]["name"].item()}'
                        vote_list.append(row)
                text += '\n\n誰の票を無効化しますか？'
                try:
                    line_bot_api.link_rich_menu_to_user(lawyer['user_id'].item(), settings.select_id)
                except:
                    pass
                items = []
                for row in vote_list:
                    items.append({
                        "type": "action",
                        "action": {
                            "type": "postback",
                            "label": f'{row["name"]}',
                            "text": f'{row["name"]} さんの票を無効にしました',
                            "data": "{'action':'lawyer_vote', 'vote':'" + row["user_id"] + "'}"
                        }
                    })
                push_message([lawyer['user_id'].item()], [{
                    "type": "text",
                    "text": text,
                    "quickReply": {
                        "items": items
                    }
                }])

            else:
                text = '<<投票結果>>'
                for index, row in vote_df.sort_values('number').iterrows():
                    if row["vote"] is None:
                        text += f'\n{row["name"]}  → 投票なし'
                    elif row['role'] == 'rich':
                        text += f'\n{row["name"]}  → {df[df["user_id"] == row["vote"]]["name"].item()}×２'
                    else:
                        text += f'\n{row["name"]}  → {df[df["user_id"] == row["vote"]]["name"].item()}'

                vote_count = vote_df['vote'].value_counts()
                rich = vote_df[vote_df['role'] == 'rich']
                if len(rich) == 1:
                    vote_count[rich['vote'].item()] += 1
                target = vote_count[vote_count == vote_count.max()].index.to_list()
                target = [df[df['user_id'] == t]['role'].item() for t in target]
                if 'murder' in target:
                    wins = ['lawyer', 'rich', 'spy', 'butler', 'guest1', 'guest2', 'guest3', 'guest4']
                else:
                    wins = ['murder', 'partner']
                if 'bomb' in target:
                    wins = ['bomb']

                text += '\n\n<<結果発表>>'
                for index, row in df.sort_values('number').iterrows():
                    text += f'\n{row["name"]}   {settings.roles[row["role"]]["name"]}'
                    if row['number'] > 0 and row["role"] in wins:
                        text += '   ☆'
                push_message(vote_df['user_id'].to_list(), [{
                    "type": "text",
                    "text": text
                }])
                roles = s.query(Roles).filter_by(game_id=my_role.game_id).all()
                for role in roles:
                    role.status = 0
                s.commit()
                for index, row in df[df['number'] > 0].iterrows():
                    try:
                        line_bot_api.link_rich_menu_to_user(row['user_id'], settings.with_room_id)
                    except:
                        pass

    data = {'replyToken': event.reply_token, 'messages': reply_json}
    res = requests.post(reply_url, data=json.dumps(data), headers=headers)


if __name__ == '__main__':
    app.run()
