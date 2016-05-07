import _thread as thread
import queue

import orchestra.util as util

AUTOCMDS = ('CursorMoved',)
CUSTOMCMDS = (),

class Orchestra(util.VimMix):
    def __init__(self, vim):
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
                                    util.play_sound,(audio,))
        thread.start_new_thread(do, (),)

    def queue_audio(self, audio):
        self._audio_queue.put(audio)
