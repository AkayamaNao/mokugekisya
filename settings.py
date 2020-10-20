# from pathlib import Path
import psycopg2
import subprocess

testmode = 0

# LINEbot
access_token = 'otgJKMZRx9vbtQ/TxWcB2dp/H9o6hgT6ycJXfdGn4+C1oduCyxgJ7BxEC/HURwDifaBA6RovMSw783VoSZJ6Dk1ocYLqVMMxTNP5mvzZhYYn9+Rv1zKYiJGHWez7XIiqzf3c/IzK+aFlvPdKKcIuVQdB04t89/1O/w1cDnyilFU='
secret_key = 'edd8e46d020640be73e63a6a3f603919'

if testmode == 1:
    db_info = 'postgres://lwubvckgoxqyug:7d0bb77b21e0cef35b450dc7ccf5a61183584fd23ee5ceff11349f34562fa12b@ec2-52-3-4-232.compute-1.amazonaws.com:5432/d2fudi9t19hirf'
    DEBUG = True
else:
    proc = subprocess.Popen('printenv DATABASE_URL', stdout=subprocess.PIPE, shell=True)
    db_info = proc.stdout.read().decode('utf-8').strip()
    DEBUG = False

# pythonanywhere
# db_uri = {
#     'user': 'akanaohub',
#     'password': 'mentaiko1',
#     'host': 'akanaohub.mysql.pythonanywhere-services.com',
#     'database': 'akanaohub$mokugekisha',
#     'charset': 'utf8mb4',
# }
# db_info='mysql+pymysql://{user}:{password}@{host}/{database}?charset={charset}'.format(**db_uri)
# DEBUG = False

SQLALCHEMY_DATABASE_URI = db_info
SQLALCHEMY_TRACK_MODIFICATIONS = True
SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
JSON_AS_ASCII = False
# UPLOADED_CONTENT_DIR = Path("upload")


none_room_id = "richmenu-7c1d4f5c559688b64c1c5f26016cc7a6"
with_room_id = "richmenu-08f7e2b3fb041520f4dada73f1dce1c0"
wait_id = "richmenu-e71a59cc5bbf69ec903eb2d47b413f07"
select_id = "richmenu-880b69d117aea070ab36835acc39c12c"

roles = {'murder': {'name': '殺人鬼', 'win': '自分がボイラー室に入らなければ勝ち', 'ability': '',
                    'richmenu': "richmenu-6b628867cc30bb86e7da35b23b67b944"},
         'partner': {'name': '共謀者', 'win': '殺人鬼がボイラー室に入らなければ勝ち', 'ability': '',
                     'richmenu': "richmenu-33f3ab00a555ee2ab0e9800713ca737a"},
         'bomb': {'name': '爆弾魔', 'win': '自分がボイラー室に入ると勝ち', 'ability': '',
                  'richmenu': "richmenu-8000ddc853596c1d0bdd2fa70b7327c7"},
         'lawyer': {'name': '弁護士', 'win': '殺人鬼をボイラー室に入れると勝ち', 'ability': '投票開示後に誰かの票を無効化\n',
                    'richmenu': "richmenu-39ca548139e9032bf5444e15ef1e6118"},
         'rich': {'name': '富豪', 'win': '殺人鬼をボイラー室に入れると勝ち', 'ability': '自分の票を2票分とする\n',
                  'richmenu': "richmenu-387a9d10b00888f2641175787890f729"},
         'spy': {'name': '探偵', 'win': '殺人鬼をボイラー室に入れると勝ち', 'ability': '相談中に正体を公開したら、即座に1人をボイラー室行きにしてゲーム終了\n',
                 'richmenu': "richmenu-27a03f1e57d0c6d1bc1a29ae7a5b03a6"},
         'butler': {'name': '執事', 'win': '殺人鬼をボイラー室に入れると勝ち', 'ability': '相談中に正体を公開したら、「伏せた2枚」を確認し、投票権を失う\n',
                    'richmenu': "richmenu-98373943d23323a98910ec9b13dc8afe"},
         'guest1': {'name': '客人（赤）', 'win': '殺人鬼をボイラー室に入れると勝ち', 'ability': '',
                    'richmenu': "richmenu-99872e04a40392de1b5414fedc5c28df"},
         'guest2': {'name': '客人（青）', 'win': '殺人鬼をボイラー室に入れると勝ち', 'ability': '',
                    'richmenu': "richmenu-a13fe8851f60c45e1f0509a695e6d1ae"},
         'guest3': {'name': '客人（黄）', 'win': '殺人鬼をボイラー室に入れると勝ち', 'ability': '',
                    'richmenu': "richmenu-af7cef71018ea6ebfddccb07b58ae0f7"},
         'guest4': {'name': '客人（黄）', 'win': '殺人鬼をボイラー室に入れると勝ち', 'ability': '',
                    'richmenu': "richmenu-af7cef71018ea6ebfddccb07b58ae0f7"},
         'guest': {'name': '客人', 'win': '殺人鬼をボイラー室に入れると勝ち', 'ability': '',
                   'richmenu': "richmenu-99872e04a40392de1b5414fedc5c28df"}
         }

# murder = "richmenu-6b628867cc30bb86e7da35b23b67b944"
# partner = "richmenu-33f3ab00a555ee2ab0e9800713ca737a"
# bomb = "richmenu-8000ddc853596c1d0bdd2fa70b7327c7"
# lawyer = "richmenu-39ca548139e9032bf5444e15ef1e6118"
# rich = "richmenu-387a9d10b00888f2641175787890f729"
# spy = "richmenu-27a03f1e57d0c6d1bc1a29ae7a5b03a6"
# butler = "richmenu-98373943d23323a98910ec9b13dc8afe"
# guest1 = "richmenu-99872e04a40392de1b5414fedc5c28df"
# guest2 = "richmenu-a13fe8851f60c45e1f0509a695e6d1ae"
# guest3 = "richmenu-af7cef71018ea6ebfddccb07b58ae0f7"

levels = [{'plus': 1, 'roles': ['murder', 'guest'], 'rule': ''},
          {'plus': 1, 'roles': ['murder', 'partner', 'guest'], 'rule': ''},
          {'plus': 1, 'roles': ['murder', 'partner', 'lawyer', 'guest'], 'rule': ''},
          {'plus': 1, 'roles': ['murder', 'bomb', 'guest'], 'rule': ''},
          {'plus': 1, 'roles': ['murder', 'bomb', 'rich', 'guest'], 'rule': ''},
          {'plus': 1, 'roles': ['murder', 'bomb', 'spy', 'guest'], 'rule': ''},
          {'plus': 3, 'roles': ['murder', 'partner', 'bomb', 'lawyer', 'rich', 'spy', 'butler', 'guest'],
           'rule': '最初に殺人鬼以外の2枚を伏せる（執事は確認できる）'},
          {'plus': 5, 'roles': ['murder', 'partner', 'bomb', 'lawyer', 'rich', 'spy', 'butler', 'guest'],
           'rule': '最初に殺人鬼以外の2枚を伏せ（執事は確認できる）、さらに2枚を除外する（誰も確認できない）'}]

numbers_levels = {3: [0, 1, 3], 4: [0, 1, 2, 3, 4, 5, 6, 7], 5: [1, 2, 3, 4, 5, 6, 7], 6: [2, 4, 5, 6, 7]}