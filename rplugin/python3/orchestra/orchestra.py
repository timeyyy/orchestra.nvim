import _thread as thread
import queue
import random
import os

import neovim

import orchestra.util as util

CUSTOMCMDS = (),
AUTOCMDS = ('CursorMoved', 'CursorMovedI')

class ThemeMix(util.VimMix):
    def __init__(self):
        super().__init__()
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
                    raise FileNotFoundError('Could not find: '
                                            + track)
        return found


class FunctionsMix(util.VimMix):
    def ensemble(self, event, *audio):
        audio = self.get_audio(audio)
        if event in CUSTOMCMDS:
            # Custom event type.. spit out into another func?
            raise NotImplementedError
        else:
            # TODO reinstate this and remove setup_functions
            # when neovim updates..
            # @neovim.autocmd(event)
            # def func(nvim):
                # self.echom('adding to queue')
                # self.queue_audio(audio)
            func_name = 'Orchestra_' + event
            # setattr(self.main, func_name, func)
            # TODO extend for multple aruguments
            # assert len(audio) == 1
            # cmd = "call {}('{}')".format(
                        # func_name, *audio)
            cmd = self._build_cmd(func_name, audio)
            self.vim.command("augroup " + func_name)
            self.vim.command("autocmd!")
            self.vim.command("autocmd {event} * {cmd}".format(
                                                   event=event,
                                                   cmd=cmd))
            self.vim.command("augroup END")
            self.main.logger.add('made new autocmd for ' + func_name)

    def _build_cmd(self, func_name, audio):
        # To handle variable length arugements 
        parts = ['call {}'.format(func_name)]
        parts.append('(')
        brackets = "'{}'," * len(audio)
        # Remove the last comma
        parts.append(brackets[:-1])
        parts.append(')')
        formatstr = ''.join(parts)
        return formatstr.format(*audio)


class Orchestra(ThemeMix, FunctionsMix):
    def __init__(self, vim, main):
        # cannot run any commands in vim, as this is 
        # called from pluging __init__, otherwise wierd
        # errors happen!!!
        super().__init__()
        self.vim = vim
        self.main = main
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
        check = util.play_sound(audio[index])
        if not check:
            raise Exception('should fail in get_audio-parts...')

    def queue_audio(self, audio):
        self._audio_queue.put(audio)
