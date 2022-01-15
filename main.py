from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage,
    MemberJoinedEvent
)
import os
import traceback
import logging
import psycopg2
import hololive
import compass

app = Flask(__name__)

# 環境変数取得
# LINE Developersで設定されているアクセストークンとChannel Secretをを取得し、設定します。
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

def get_connection():
    dsn = "host=ec2-34-201-95-87.compute-1.amazonaws.com port=5432 dbname=dcknjc81kjsjse user=vdueywviqryxbs password=be8a79c3d3b7c0e1ec0c26119627f45081f7ac3e8472b60af5fb8405f4b1f468"
    return psycopg2.connect(dsn)

def get_response_message():
    with get_connection() as conn:
        with conn.cursor(name="cs") as cur:
            try:
                sql_Str = "SELECT TO_CHAR(CURRENT_DATE, 'yyyy/mm/dd');"
                cur.execute(sql_Str)
                (mes,) = cur.fetchone()
                return mes
            except Exception:
                mes = "exception"
                return mes

def set_greeting(gid,text):
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                sql_Str = "INSERT INTO group_info(group_id, join_message, switch) VALUES(%s, %s, %s)", (gid, text, True)
                cur.execute(*sql_Str)
                mes = f"挨拶を「{text}」に設定しました"
                return mes
            except Exception as error:
                print(error)
                mes = "exception"
                return mes

def check_greeting(gid):
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                sql_Str = "SELECT switch FROM group_info WHERE group_id=%s"
                vars = str(gid)
                cur.execute(sql_Str, (vars,))
                (mes,) = cur.fetchone()
                return mes
            except Exception as error:
                print(error)
                print("1")
                return False

def get_greeting(gid):
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                sql_Str = "SELECT join_message FROM group_info WHERE group_id=%s"
                vars = str(gid)
                cur.execute(sql_Str, (vars,))
                (mes,) = cur.fetchone()
                return mes
            except Exception as error:
                print(error)
                print("2")
                return "None"

# Webhookからのリクエストをチェックします。
@app.route("/callback", methods=['POST'])
def callback():
    # リクエストヘッダーから署名検証のための値を取得します。
    signature = request.headers['X-Line-Signature']

    # リクエストボディを取得します。
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    # 署名を検証し、問題なければhandleに定義されている関数を呼び出す。
    try:
        handler.handle(body, signature)
    # 署名検証で失敗した場合、例外を出す。
    except InvalidSignatureError:
        abort(400)
    # handleの処理を終えればOK
    return 'OK'


# LINEでMessageEvent（普通のメッセージを送信された場合）が起こった場合に、
# def以下の関数を実行します。
# reply_messageの第一引数のevent.reply_tokenは、イベントの応答に用いるトークンです。
# 第二引数には、linebot.modelsに定義されている返信用のTextSendMessageオブジェクトを渡しています。

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        msg = event.message.text
        if msg == "test":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="ok"))
        if msg == "hololive":
            if hololive.scrape() is None:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="今は誰も配信していません"))
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(alt_text='hololive', contents=hololive.scrape()))
        if msg == "compass":
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text='compass', contents=compass.gacha()))
        if msg == "uid":
            uid = event.source.user_id
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=uid))
        if "uid" in msg and "@" in msg:
            users = event.message.mention.mentionees
            mbox = ""
            for user in users:
                profile = line_bot_api.get_profile(user.user_id)
                txt = f"[{profile.display_name}]\n{user.user_id}\n"
                mbox += txt
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=mbox))
        if msg == "gid" and event.source.type == 'group':
            gid = event.source.group_id
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=gid))
        if msg == "profile":
            uid = event.source.user_id
            profile = line_bot_api.get_profile(uid)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"name:{profile.display_name}\nstatus_message:{profile.status_message}\npicture:{profile.picture_url}"))
        if msg == "group" and event.source.type == 'group':
            gid = event.source.group_id
            g_summary = line_bot_api.get_group_summary(gid)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"name:{g_summary.group_name}\nGreeting:{get_greeting(gid)}\npicture:{g_summary.picture_url}"))
        if msg == "bot":
            bot_info = line_bot_api.get_bot_info()
            print(bot_info, type(bot_info))
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=bot_info.display_name))
        if msg == "time":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=get_response_message()))
        if "greeting:" in msg:
            txt = msg.replace("greeting:","")
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=set_greeting(event.source.group_id, txt)))
        if msg == "follower":
            print(line_bot_api.get_followers_ids())
    except Exception:
        print(traceback.format_exc())

@handler.add(MemberJoinedEvent)
def handler_join(event):
    if check_greeting(event.source.group_id):
        line_bot_api.push_message(event.source.group_id, TextSendMessage(text=get_greeting(event.source.group_id)))


# ポート番号の設定
if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    #    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
