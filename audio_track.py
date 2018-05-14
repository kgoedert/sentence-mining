import argparse
import requests
import json
import urllib.request
import os
from pydub import AudioSegment
from natsort import natsorted

URL = "https://api.soundoftext.com"

def main():
    parser = argparse.ArgumentParser("Sentence Mining")
    parser.add_argument("source_file", help="File containing the phrases.")
    parser.add_argument("tl", help="Target Language")

    args = parser.parse_args()
    dictionary = parse_sentences(args.source_file)

    create_audio(dictionary, args.tl)

    combine_audio_files()

def findFilesInFolder(path, pathList, extension, subFolders = True):
    """  Recursive function to find all files of an extension type in a folder (and optionally in all subfolders too)

    path:        Base directory to find files
    pathList:    A list that stores all paths
    extension:   File extension to find
    subFolders:  Bool.  If True, find files in all subfolders under path. If False, only searches files in the specified folder
    """

    try:   # Trapping a OSError:  File permissions problem I believe
        for entry in os.scandir(path):
            if entry.is_file() and entry.path.endswith(extension):
                pathList.append(entry.path)
            elif entry.is_dir() and subFolders:   # if its a directory, then repeat process as a nested function
                pathList = findFilesInFolder(entry.path, pathList, extension, subFolders)
    except OSError:
        print('Cannot access ' + path +'. Probably a permissions error')

    return pathList

def combine_audio_files():
    half_second_silence = AudioSegment.silent(duration=500)
    two_seconds_silence = AudioSegment.silent(duration=2000)
    files_path = []

    findFilesInFolder('/home/kelly/repositories/sentence mining/output', files_path, '.mp3', True) 
    files_path = natsorted(files_path)

    print(files_path)

    output =  AudioSegment.empty()

    for index, file in enumerate(files_path):
        if index == 0:
            output = AudioSegment.from_file(file)
        elif index % 2 != 0:
            output = output + half_second_silence + AudioSegment.from_file(file)
        elif index % 2 == 0:
            output = output + two_seconds_silence + AudioSegment.from_file(file)
    
    output.export('output/output.mp3', format='mp3')
    print('file created')

def create_audio(dictionary, tl):
    i = 0
    for key in dictionary:
        get_audio(key, 'en', 'output/' + str(i) + '.mp3')
        i += 1
        get_audio(dictionary[key], tl, 'output/' + str(i) + '.mp3')
        i += 1


def parse_sentences(file) -> 'dict':
    lines = open(file).read().splitlines()

    dict = {}
    for line in range(0, len(lines), 3) :
        if lines[line].startswith('#'):
            continue
        dict[lines[line + 1]] = lines[line]
    
    return dict

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


def get_audio(input_text='',language='en', output='output.mp3'):
    voice = chose_voice(language)
    post = {"engine": "Google", 
        "data": {
            "text": input_text,
            "voice": voice
        }
    }

    response = requests.post(URL + '/sounds', json=post)
    data = json.loads(response.text)

    if data['success'] == True:
        file_location = requests.get(URL + "/sounds/" + data['id'])
        file_location_res = json.loads(file_location.text)

        if file_location_res['status'] == 'Done':
            urllib.request.urlretrieve(file_location_res['location'], output)
            print("Text downloaded: %s" % (input_text))
        else:
            print("Cant get sound file for: %s " % (input_text))    
    else:
        print("Cant get sound file for: %s " % (input_text))


if __name__ == '__main__':
    main()

