import _thread as thread
import queue
import random
import os

import orchestra.util as util

CUSTOMCMDS = (),

# class used just for seperation of logic
class Theme(util.VimMix):
    def __init__(self):
        self.audio_paths = {}
        self.audio_paths[None] = os.path.dirname(__file__)
        self.theme = None

    def set_theme(self, theme):
        '''
        runs the theme file, registering stuff to do
        '''
        self.theme = theme
        self.theme_path = 'autoload'
        self.vim.command('runtime! {0}/{1}.vim'.format(
                                        self.theme_path,
                                        theme))

    def add_path(self, abs_path_theme):
        '''
        registers the theme so we know which
        paths to look in for audio files
        '''
        theme = os.path.basename(abs_path_theme)
        theme = os.path.splitext(theme)[0]
        path = os.path.dirname(abs_path_theme)
        self.audio_paths[theme] = path

    def get_audio(self, audio):
        '''
        returns all audio parts with absolute paths

        the current theme has priority, otherwise
        search all other paths
        '''
        # TODO COPY IN THE THE TRACK IF IT DOESNT 
        # EXIST IN THE THEME THAT IS USING IT
        # TODO if multiple tracks with a name exist
        # and md5 differ
        # and we have to copy one in then just
        # raise an error..
        found = []
        theme_path = self.audio_paths[self.theme]
        for track in audio:
            audio_parts = util.get_audio_parts(
                                os.path.join(theme_path, track))
            if audio_parts:
                found.extend(audio_parts)
            else:
                # TODO this is untested :( 
                for theme, path in self.audio_paths.items():
                    audio_parts = util.get_audio_parts(
                                    os.path.join(path, track))
                    if audio_parts:
                        found.extend(audio_parts)
                        break
                else:
                    raise ValueError('Could not find ' + track)
        return found


class Orchestra(Theme):
    def __init__(self, vim):
        # cannot run any commands in vim, as this is 
        # called from pluging __init__, otherwise wierd
        # errors happen!!!
        super().__init__()
        self.vim = vim
        self._audio_queue = queue.Queue()
        self.consume()

    def consume(self):
        def do():
            while True:
                try:
                    audio = self._audio_queue.get(block=True)
                except queue.Empty:
                    pass
                else:
                    thread.start_new_thread(
                                    self._play_sound, (audio,))
        thread.start_new_thread(do, (),)

    def _play_sound(self, audio):
        # Pick audio from random
        index = random.randint(0, len(audio)-1)
        util.play_sound(audio[index])

    def queue_audio(self, audio):
        self._audio_queue.put(audio)
