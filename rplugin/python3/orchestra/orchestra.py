
import orchestra.util as util

class Orchestra():
    def __init__(self, vim):
        self.vim = vim

    def cursor_moved(self):
        util.play_sound('woosh.wav')

    def position_has_changed(self, pos):
        return (pos != self.vim.current.window.cursor or
                self.vim.funcs.mode() != 'i')
