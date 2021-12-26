import random
import json


def gacha():
    with open("hero.json", "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)

    num = str(random.randrange(59))
    return flexdata(json_data[num])


def flexdata(data):
    template = {
        "type": "bubble",
        "hero": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": data["name"],
                    "align": "center",
                    "weight": "bold",
                    "color": "#FFFFFF"
                }
            ],
            "backgroundColor": "#000000"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "image",
                    "size": "80%",
                    "url": data["img"],
                    "aspectMode": "fit",
                    "align": "center",
                    "margin": "none"
                }
            ],
            "paddingAll": "none",
            "height": "200px",
            "borderWidth": "none",
            "cornerRadius": "none",
            "background": {
                "type": "linearGradient",
                "angle": "0deg",
                "startColor": "#000000",
                "endColor": "#ffffff"
            },
            "spacing": "none",
            "margin": "none",
            "justifyContent": "center"
        }
    }
    return template
