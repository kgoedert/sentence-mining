import argparse
import requests
import json
import urllib.request
import base64
import time
import re


url = "https://api.soundoftext.com"
ANKI_URL = "http://192.168.0.23:8766"

def main():
    parser = argparse.ArgumentParser("Sentence Mining")
    parser.add_argument("source_file", help="File containing the phrases.")
    parser.add_argument("tl", help="Target Language")
    parser.add_argument("deck", help="Anki deck name")

    args = parser.parse_args()

    dictionary = parse_sentences(args.source_file)
    
    create_anki_cards(dictionary, args.tl, args.deck)

def parse_sentences(file) -> 'dict':
    lines = open(file).read().splitlines()

    dict = {}
    for line in range(0, len(lines), 3) :
        if lines[line].startswith('#'):
            continue
        dict[lines[line]] = lines[line + 1]
    
    return dict

def get_audio(input_text='',language='en', output='output.mp3'):
    voice = chose_voice(language)
    post = {"engine": "Google", 
        "data": {
            "text": input_text,
            "voice": voice
        }
    }

    response = requests.post(url + '/sounds', json=post)
    data = json.loads(response.text)

    if data['success'] == True:
        file_location = requests.get(url + "/sounds/" + data['id'])
        file_location_res = json.loads(file_location.text)

        if file_location_res['status'] == 'Done':
            urllib.request.urlretrieve(file_location_res['location'], output)
            print("Text downloaded: %s" % (input_text))
        else:
            print("Cant get sound file for: %s " % (input_text))    
    else:
        print("Cant get sound file for: %s " % (input_text))

def chose_voice(language) -> str:
    lang = ''
    
    if language == 'fr':
        lang = 'fr-FR'
    elif language == 'de':
        lang = 'de-DE'
    elif language == 'es':
        lang = 'es-ES'
    else:
        lang = 'en-US'

    return lang

    
    
def create_anki_cards(dictionary, tl, deck):
    for key in dictionary:
        name_without_spaces = key.replace(' ', '_')
        output_file = 'output/' + name_without_spaces + '.mp3'

        get_audio(key, tl, output_file)
        
        base64 = mp3_to_base64(output_file)
        anki_file_name = upload_mp3_to_anki(name_without_spaces, base64)

        card = create_card(dictionary[key], key, anki_file_name, deck)

        response = requests.post(ANKI_URL, json=card)

        if response.status_code != 200:
            print('Could not add card to anki')
        else:
            print("Card successfully added to anki")


def create_card(phrase_en, phrase_tl, sound_file, deck):
    card = {}

    card['action'] = "addNote"
    card['version'] = 5
    card['params'] = {}
    card['params']['note'] = {}
    card['params']['note']['deckName'] = deck
    card['params']['note']['modelName'] = "3. All-Purpose Card"
    card['params']['note']['fields'] = {}
    card['params']['note']['fields']['Front (Example with word blanked out or missing)'] = phrase_en + '[sound:' + sound_file + ']'
    card['params']['note']['fields']['Back (a single word/phrase, no context)'] = phrase_en
    card['params']['note']['fields']['- The full sentence (no words blanked out)'] = phrase_tl
    card['params']['note']['fields']['• Make 2 cards? ("y" = yes, blank = no)'] = 'y'

    return card

def mp3_to_base64(file_path):
    f = open(file_path, 'rb')
    encoded = base64.b64encode(f.read())
    f.close()
    

    return encoded.decode()

def upload_mp3_to_anki(filename, file_base64):
    name_millis = "_" + str(int(round(time.time() * 1000))) + ".mp3"

    content = {"action": "storeMediaFile", "version": 5, "params": {"filename": name_millis, "data": file_base64}}
    response = requests.post(ANKI_URL, json=content)

    if response.status_code != 200:
        print('Could not upload mp3 file to anki')
    else:
        print("File '%s' uploaded to anki. " % (name_millis))
    return name_millis

if __name__ == '__main__':
    main()