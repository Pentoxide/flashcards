"""
Downloads, parses, and compiles data for flashcards from flashcardo.com
Input: language
Output: compiled deck in data.json file, audio file for each card
"""
import os
import sys
import re
import json
import random
import string
import urllib.request
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

def generate_deck():
    """Generates random deck id"""
    letters = string.ascii_lowercase
    letters += string.ascii_uppercase
    letters += string.digits
    return ''.join(random.choice(letters) for i in range(8))

def get_block(language, i):
    """Downloading 50 word block from url"""
    j = i*50-49
    k = i*50
    url = f'https://flashcardo.com/{language}-flashcards/f/{j}-{k}/1'
    req = Request(
        url=url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urlopen(req) as remote:
        response = remote.read()
    output = response.decode("utf8")
    soup = BeautifulSoup(output, 'html.parser')
    script = soup.body.find('script').text
    with open(f'{PATH}/{i}.js', 'w', encoding="utf-8") as file:
        file.write(script)

def parse_file(filename):
    """Load file and parse some errors"""
    with open(filename, 'r', encoding="utf-8") as file:
        p = re.compile('var.*?=s*(.*?);')
        if filename == f'{PATH}/14.js':
            fix = file.read().replace('x &lt; y', 'x < y')
            parsed = p.findall(fix)
        else:
            parsed = p.findall(file.read())
        data = json.loads(parsed[0])
    return data

def get_audio(entry):
    """Download audio if there is none"""
    filename = f"{entry['audio']}.mp3"
    audio_path = f'{PATH}/audio'
    full_path = f"{audio_path}/{filename}"
    if not os.path.isfile(full_path):
        urllib.request.urlretrieve(
            f"https://flashcardo.com/audio/{entry['sid_audio']}/{filename}",
            f"{full_path}"
            )
    size = os.path.getsize(full_path)
    return (filename, size)

def compile_card(deck, card_order, entry):
    """Compiles one card according to the standart"""
    audio_filename, audio_size = get_audio(entry)
    position = f"{card_order:04d}"
    english = f"{entry['from']}"
    hint = f"{entry['fromhint']}"
    if hint != "":
        english += f" ({hint})"
    target = f"{entry['word']}"
    return (
        f'{{"~:content":"{english}\\n---\\n {target}'
        f'![{audio_filename}]({audio_filename})",'
        f'"~:deck-id":"~:{deck}",'
        f'"~:attachments":{{"{audio_filename}":{{"~:size":{audio_size},'
        f'"~:type":"audio/mpeg"}}}},"~:pos":"{position}"}},'
    )

def fill_body(language, deck):
    """Process files and compiles the list of cards"""
    order = 1
    body = ''
    for block in range(1, 21):
        filepath = f'{PATH}/{block}.js'
        if not os.path.isfile(filepath):
            print(f'Getting {block} block...')
            get_block(language, block)
        else:
            print(f'{filepath} exist, skipping...')
        print(f'Processing {block}...')
        result = parse_file(filepath)
        for item in result:
            card = compile_card(deck, order, item)
            body += card
            order += 1
    return body[:-1]

if __name__ == "__main__":
    lang = sys.argv[1]
    PATH = f'data/{lang}'
    DECK_ID = generate_deck()
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)
    HEADER = (
        f'{{"~:version":2,"~:decks":[{{"~:id":"~:{DECK_ID}",'
        f'"~:name":"{lang.title()} 1000","~:cards":{{"~#list":['
    )
    FOOTER = ']}}]}'
    try:
        os.mkdir(PATH)
    except FileExistsError:
        pass
    with open(f'{PATH}/data.json', 'w', encoding="utf-8") as datafile:
        datafile.write(HEADER+fill_body(lang, DECK_ID)+FOOTER)
