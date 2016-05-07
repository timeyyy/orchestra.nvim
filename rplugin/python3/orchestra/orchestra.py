import _thread as thread
import queue
import random

import orchestra.util as util

CUSTOMCMDS = (),

class Orchestra(util.VimMix):
    def __init__(self, vim):
        self.vim = vim
        self._audio_queue = queue.Queue()
        self.consume()
        self.load_theme()

    def consume(self):
        def do():
            while True:
                try:
                    audio = self._audio_queue.get(block=True)
                except queue.Empty:
                    pass
                else:
                    thread.start_new_thread(
                                    self._play_sound,(audio,))
        thread.start_new_thread(do, (),)

    def _play_sound(self, audio):
        # Pick an auido from random
        index = random.randint(0, len(audio)-1)
        util.play_sound(audio[index])
    
    def queue_audio(self, audio):
        self._audio_queue.put(audio)

    def load_theme(self):
        theme = self.vim.eval('g:orchestra#symphony')
        self.echom(theme)
        # self.vim.command('source {0}/{0}.vim'.format(theme))
        
