""" Memes - To make one, go to https://imgflip.com/memegenerator and click Upload new template """

import json
import os

import requests

MEMELIB = [
    {
        "infoUrl": "https://imgflip.com/memetemplate/385045951/Jopacall",
        "name": "Jopacall",
        "templateID": 385045951,
        "format": "png",
        "dimensions": "833x711 px",
        "filesize": "581 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Conspiracy-Keanu",
        "name": "Conspiracy Keanu",
        "templateID": 61583,
        "format": "jpg",
        "dimensions": "551x549 px",
        "filesize": "28 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Woman-Yelling-At-Cat",
        "name": "Woman Yelling At Cat",
        "templateID": 188390779,
        "format": "jpg",
        "dimensions": "680x438 px",
        "filesize": "33 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/One-Does-Not-Simply",
        "name": "One Does Not Simply",
        "templateID": 61579,
        "format": "jpg",
        "dimensions": "568x335 px",
        "filesize": "32 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Surprised-Pikachu",
        "name": "Surprised Pikachu",
        "templateID": 155067746,
        "format": "jpg",
        "dimensions": "1893x1893 px",
        "filesize": "91 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Grandma-Finds-The-Internet",
        "name": "Grandma Finds The Internet",
        "templateID": 61556,
        "format": "jpg",
        "dimensions": "640x480 px",
        "filesize": "42 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Doge",
        "name": "Doge",
        "templateID": 8072285,
        "format": "jpg",
        "dimensions": "620x620 px",
        "filesize": "29 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Third-World-Success-Kid",
        "name": "Third World Success Kid",
        "templateID": 101287,
        "format": "jpg",
        "dimensions": "500x500 px",
        "filesize": "32 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Third-World-Skeptical-Kid",
        "name": "Third World Skeptical Kid",
        "templateID": 101288,
        "format": "jpg",
        "dimensions": "426x426 px",
        "filesize": "79 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/177682295/You-Guys-are-Getting-Paid",
        "name": "You Guys are Getting Paid",
        "templateID": 177682295,
        "format": "jpg",
        "dimensions": "520x358 px",
        "filesize": "170 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/The-Most-Interesting-Man-In-The-World",
        "name": "The Most Interesting Man In The World",
        "templateID": 61532,
        "format": "jpg",
        "dimensions": "550x690 px",
        "filesize": "48 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Jack-Sparrow-Being-Chased",
        "name": "Jack Sparrow Being Chased",
        "templateID": 460541,
        "format": "jpg",
        "dimensions": "500x375 px",
        "filesize": "25 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Brace-Yourselves-X-is-Coming",
        "name": "Brace Yourselves X is Coming",
        "templateID": 61546,
        "format": "jpg",
        "dimensions": "622x477 px",
        "filesize": "41 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/That-Would-Be-Great",
        "name": "That Would Be Great",
        "templateID": 563423,
        "format": "jpg",
        "dimensions": "526x440 px",
        "filesize": "31 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/See-Nobody-Cares",
        "name": "See Nobody Cares",
        "templateID": 6531067,
        "format": "jpg",
        "dimensions": "620x676 px",
        "filesize": "70 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/And-Just-Like-That",
        "name": "And Just Like That",
        "templateID": 54401824,
        "format": "jpg",
        "dimensions": "1012x675 px",
        "filesize": "146 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Success-Kid",
        "name": "Success Kid",
        "templateID": 61544,
        "format": "jpg",
        "dimensions": "500x500 px",
        "filesize": "11 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Creepy-Condescending-Wonka",
        "name": "Creepy Condescending Wonka",
        "templateID": 61582,
        "format": "jpg",
        "dimensions": "550x545 px",
        "filesize": "48 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Dr-Evil-Laser",
        "name": "Dr Evil Laser",
        "templateID": 40945639,
        "format": "jpg",
        "dimensions": "500x405 px",
        "filesize": "25 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Put-It-Somewhere-Else-Patrick",
        "name": "Put It Somewhere Else Patrick",
        "templateID": 61581,
        "format": "jpg",
        "dimensions": "343x604 px",
        "filesize": "49 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Matrix-Morpheus",
        "name": "Matrix Morpheus",
        "templateID": 100947,
        "format": "jpg",
        "dimensions": "500x303 px",
        "filesize": "28 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Sparta-Leonidas",
        "name": "Sparta Leonidas",
        "templateID": 195389,
        "format": "jpg",
        "dimensions": "500x264 px",
        "filesize": "29 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/92084495/Charlie-Conspiracy-Always-Sunny-in-Philidelphia",
        "name": "Charlie Conspiracy",
        "templateID": 92084495,
        "format": "jpg",
        "dimensions": "1024x768 px",
        "filesize": "133 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Buddy-Christ",
        "name": "Buddy Christ",
        "templateID": 17699,
        "format": "jpg",
        "dimensions": "400x400 px",
        "filesize": "30 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/4081988/What-if-i-told-you",
        "name": "What if i told you",
        "templateID": 4081988,
        "format": "jpg",
        "dimensions": "334x302 px",
        "filesize": "18 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/96633334/Guess-Ill-die",
        "name": "Guess I'll die",
        "templateID": 96633334,
        "format": "jpg",
        "dimensions": "384x313 px",
        "filesize": "77 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/80964944/Woody-and-Buzz-Lightyear-Everywhere-Widescreen",
        "name": "Woody and Buzz",
        "templateID": 80964944,
        "format": "jpg",
        "dimensions": "2524x1420 px",
        "filesize": "189 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Success-Kid-Original",
        "name": "Success Kid Original",
        "templateID": 341570,
        "format": "jpg",
        "dimensions": "500x333 px",
        "filesize": "20 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Confused-Gandalf",
        "name": "Confused Gandalf",
        "templateID": 673439,
        "format": "jpg",
        "dimensions": "500x607 px",
        "filesize": "28 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/I-Was-Told-There-Would-Be",
        "name": "I Was Told There Would Be",
        "templateID": 2372682,
        "format": "jpg",
        "dimensions": "590x462 px",
        "filesize": "45 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/209713400/Baby-Yoda",
        "name": "Baby Yoda",
        "templateID": 209713400,
        "format": "jpg",
        "dimensions": "720x720 px",
        "filesize": "175 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/128916024/Its-Free-Real-Estate",
        "name": "It's Free Real Estate Template",
        "templateID": 128916024,
        "format": "jpg",
        "dimensions": "500x385 px",
        "filesize": "20 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Thats-a-paddlin",
        "name": "That's a paddlin",
        "templateID": 5265532,
        "format": "jpg",
        "dimensions": "500x361 px",
        "filesize": "21 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/16800898/But-it-was-me-Dio",
        "name": "But it was me Dio",
        "templateID": 16800898,
        "format": "jpg",
        "dimensions": "620x349 px",
        "filesize": "25 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Archer",
        "name": "Archer",
        "templateID": 10628640,
        "format": "jpg",
        "dimensions": "620x567 px",
        "filesize": "42 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Scumbag-Steve",
        "name": "Scumbag Steve",
        "templateID": 61522,
        "format": "jpg",
        "dimensions": "500x500 px",
        "filesize": "28 KB",
    },
    {
        "infoUrl": "https://imgflip.com/memegenerator/294431474/Fabiobr",
        "name": "Fabiobr Fabior",
        "templateID": 294431474,
        "format": "jpg",
        "dimensions": "680x438 px",
        "filesize": " KB",
    },
    {
        "infoUrl": "https://imgflip.com/memetemplate/Sleeping-Shaq",
        "name": "Sleeping Shaq",
        "templateID": 99683372,
        "format": "jpg",
        "dimensions": "640x631 px",
        "filesize": "56 KB",
    },
]


def find_meme(search_term):
    for m in MEMELIB:
        if search_term.lower() in m["name"].lower():
            return m
    return None


def build_meme(template_id, text0, text1):
    try:
        response = requests.post(
            url="https://api.imgflip.com/caption_image",
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            },
            data={
                "template_id": str(template_id),
                "username": os.environ["IMGFLIP_USER"],
                "password": os.environ["IMGFLIP_PW"],
                "text0": text0,
                "text1": text1,
            },
        )
        output = json.loads(response.content)
        if output["success"] == False:
            raise Exception(output["error_message"])
        return output["data"]["url"]
    except requests.exceptions.RequestException:
        print("HTTP Request failed")
