import random,json

with open("hero.json", "r",encoding="utf-8") as json_file:
    json_data = json.load(json_file)

    num = str(random.randrange(59))
    print(json_data[num])