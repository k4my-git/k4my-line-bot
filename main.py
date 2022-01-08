from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, RichMenu, RichMenuArea, RichMenuBounds, RichMenuSize, URIAction, events
)
import os
import logging
import hololive
import compass

app = Flask(__name__)

# 環境変数取得
# LINE Developersで設定されているアクセストークンとChannel Secretをを取得し、設定します。
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


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
                print(profile)
                txt = f"[{profile.display_name}]\n{user.user_id}\n"
                mbox.append(txt)
            print(mbox)
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
                TextSendMessage(text=f"name:{g_summary.group_name}\npicture:{g_summary.picture_url}"))
        if msg == "bot":
            bot_info = line_bot_api.get_bot_info()
            print(bot_info, type(bot_info))
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=bot_info.display_name))
        if msg == "richmenu":
            rich_menu_to_create = RichMenu(
                size=RichMenuSize(width=2500, height=843),
                selected=False,
                name="Nice richmenu",
                chat_bar_text="Tap here",
                areas=[RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=0, width=2500, height=843),
                    action=URIAction(label='Go to line.me', uri='https://line.me'))]
                )
            rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
            print(rich_menu_id)
            line_bot_api.set_default_rich_menu(rich_menu_id)
    except Exception as error:
        print(error)


# ポート番号の設定
if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    #    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
