# python RegEX for string pattern
import re
from datetime import datetime
from os import startfile, system, name
# path superstore is different on MacOs or Windows so use path to get path with system's default separator
from pathlib import Path
from random import choice
from webbrowser import open

from pyjokes import get_joke
# method to get TTs engine(text to Speech)
from pyttsx3 import init
from pywhatkit import playonyt, search
from speech_recognition import UnknownValueError, RequestError, Recognizer, Microphone
# searches online articles from https://wikipedia.com
from wikipedia import summary
from wikipedia.exceptions import PageError, DisambiguationError, WikipediaException


class Data:
    def __init__(self):
        # set you computer's music or video path to play
        self.MUSIC_FOLDER_PATH = 'C:\\Users\\RAHUL\\Music'
        self.MOVIE_FOLDER_PATH = 'C:\\Users\\RAHUL\\Videoes'
        # set int value 0 or 1, male or female voice '0' for DAVID, '1' for ZERA on Windows os
        self.ASSISTANT = 0
        self.VOLUME = 1.0
        self.RATE_OF_SPEECH = 140
        self.VSCODE_PAth = 'C:\\Users\\RAHUL\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe'
        self.CHROME_PATH = 'C:\\Users\\RAHUL\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe'
        # some regex object for analyzing command pattern. Those are going to be used later to make this program
        # efficient
        self._CHANGE_VOICE = re.compile(r'change(.*)? voice')
        self._VSCODE_REGEX = re.compile(r'open (code|visual studio)')
        self._VIDEO_REGEX = re.compile(r'play (video(s)?|movies(s)?)')
        self._BROWSER_REGEX = re.compile(r'open (chrome|browser)')
        self._QUESTION_REGEX = re.compile(r'(what is|how to (w+)?|who (is|are)|when|why|where|^is|^do|^does|if)')
        self._AUDIO_REGEX = re.compile(r'play (song(s)?|music(s)?|audio)')
        # if the command contains 'was' it should not tell the current date or time
        self._INTRODUCTION = re.compile(r'your name|who are you')
        self._DATE_REGEX = re.compile(r'^(?!.*was).*date')
        self._TIME_REGEX = re.compile(r'^(?!.*was).*time')
        self._EXIT_REGEX = re.compile(r'exit|sleep|quit|turn off')
        self._ON_YOUTUBE = re.compile(r'(play )?(.*) (on youtube)$')
        self._WEBSITE = re.compile(r'open (.*\.(com|in|org|dev|info|gov.in|net))')


class VoiceAssistant(Data):
    def __init__(self):
        Data.__init__(self)
        # Constructs a new TTS engine instance or reuses the existing instance for
        self.__ENGINE = init()
        self.__setProperties()
        self.__recognizer = Recognizer()
        # sets a mic to be used among a list of available mics on the device. By passing device_index we can set
        # according to us
        self.__mic = Microphone()

    def start(self) -> None:
        # if user changes those member variable and do not set the required type
        assert isinstance(self.VOLUME, float), "please set a 'float' value between 0.0 to 1.0'"
        assert isinstance(self.MUSIC_FOLDER_PATH, str), "please set a 'str' path to your music directory"
        assert isinstance(self.MOVIE_FOLDER_PATH, str), "please set a 'str' path to your video directory"
        assert isinstance(self.CHROME_PATH, str), "please set a 'str' path to your app's target or browser_name.exe"
        assert isinstance(self.VSCODE_PAth, str), "please set a 'str' path to your app's target or text_editor_name.exe"
        while True:
            command = self.__listenAndConvertToText()
            if self._EXIT_REGEX.search(command) is not None:
                print(f'\033[1;35mYOU: \033[1;34m{command}')
                self.speak('OK..have a good day')
                break
            elif command != '':
                print(f'\033[1;35mYOU: \033[1;34m{command}')
                # breakdown the command
                self.__responseOn(command)

    def __setProperties(self) -> None:
        self.__ENGINE.setProperty('volume', self.VOLUME)
        self.voices = self.__ENGINE.getProperty('voices')
        self.__ENGINE.setProperty('voice', self.voices[self.ASSISTANT].id)
        self.__ENGINE.setProperty('rate', self.RATE_OF_SPEECH)

    def __listenAndConvertToText(self) -> str:
        text = ""
        with self.__mic as source:
            self.__recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print('\033[1;32m                         listening...')
            audioData = self.__recognizer.listen(source)
        # Recognize user voice input through google speech recognition APIs
        try:
            text = self.__recognizer.recognize_google(audioData, language='en-IN')
        except RequestError:
            self.speak('looks like you have not connected your device to internet.')
            raise RequestError('try connecting your device to internet')
        except UnknownValueError:
            pass
        finally:
            if name == 'nt':
                system('cls')  # for windows
            else:
                system('clear')  # for Mac or Linux
            return text.lower()

    def speak(self, words) -> None:
        if isinstance(words, str):
            print(f'\33[1;35mAssistant: \33[1;34m{words}')
            self.__ENGINE.say(words)
            self.__ENGINE.runAndWait()
        else:
            print('argument must be a string')

    def __playSong(self) -> None:
        """lists all .mp3 files available to provided directory. Customise this path with the path where """
        song_list = list(Path(self.MUSIC_FOLDER_PATH).glob('*.mp3'))
        if len(song_list) != 0:
            startfile(str(choice(song_list)))
        else:
            self.speak('looks like.......you have no songs in this folder')

    def __playMovie(self) -> None:
        """lists all .mkv files available to provided directory. Customise this path with the path where """
        movie_list = list(Path(self.MOVIE_FOLDER_PATH).glob('*.mkv'))
        if len(movie_list) != 0:
            startfile(str(choice(movie_list)))
        else:
            self.speak('looks like.......you have no video in this folder')

    # _____________________________________________ conditions ___________________________________________#

    def __responseOn(self, command) -> None:
        play_yt = self._ON_YOUTUBE.search(command)
        site = self._WEBSITE.search(command)
        question = self._QUESTION_REGEX.search(command)

        # condition
        if play_yt is not None:
            # play desired video on YOUTUBE
            playonyt(play_yt.group(2))

        elif self._CHANGE_VOICE.search(command) is not None:
            self.speak('sure..')
            self.ASSISTANT = (1 if self.ASSISTANT == 0 else 0)
            self.__ENGINE.setProperty('voice', self.voices[self.ASSISTANT].id)
            self.speak('This is my new voice, I hope you like that')
        elif 'joke' in command:
            self.speak(get_joke())

        elif 'search' in command:
            search(command.replace('search', ''))

        elif 'what can you do' in command:
            self.speak('I can do tasks like opening vscode, browser, playing music or videoes, search on wikipedia or'
                       ' on google, and playing videoes on youtube, just say "play video name on youtube", '
                       '"open <any website name>", "open code", "play music or movie","search something" and if you '
                       'want me to turned off just say "sleep"'
                       )

        elif self._INTRODUCTION.search(command) is not None:
            self.speak('Oh no!! this question is very hard for me, by the way,'
                       f'i am {"david" if self.ASSISTANT == 0 else "zera"} '
                       'your sweetest voice assistant')

        elif self._WEBSITE.search(command) is not None:
            url = site.group(1)
            self.speak(f'opening {url}')
            open(url)

        elif 'love you' in command:
            self.speak("If I could say how much I love you in mere words, I might be able to talk more")

        elif 'how are you' in command:
            self.speak('I was fine until you asked me this')

        elif self._TIME_REGEX.search(command) is not None:
            self.speak(f"currently it's {datetime.now().strftime('%I %M %p')}")

        elif self._DATE_REGEX.search(command) is not None:
            self.speak(f"today is {datetime.now().strftime('%A %B %Y')}")

        elif self._AUDIO_REGEX.search(command) is not None:
            self.__playSong()

        elif question is not None:
            self.speak(f"Searching result for {command}")
            try:
                self.speak(summary(command.replace(question.group(1), ''), sentences=3))
            except PageError:
                self.speak(f"No page found on wikipedia for {command}")
            except DisambiguationError:
                self.speak(f"Which one do you need I am so confused")
            except WikipediaException:
                print('An Unknown error occurred while searching')

        elif self._BROWSER_REGEX.search(command) is not None:
            startfile(self.CHROME_PATH)

        elif self._VSCODE_REGEX.search(command) is not None:
            startfile(self.VSCODE_PAth)

        elif self._VIDEO_REGEX.search(command) is not None:
            self.__playMovie()

        else:
            self.speak(f'I did not understand.."{command}"')


# ______________________________________THE END_______________________________________#


if __name__ == "__main__":
    AI = VoiceAssistant()
    AI.start()
