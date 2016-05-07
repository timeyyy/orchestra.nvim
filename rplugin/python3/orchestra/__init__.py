
import neovim

import orchestra.orchestra as orch

@neovim.plugin
class Main(object):
    def __init__(self, vim):
        self.vim = vim
        self.orch = orch.Orchestra(vim)

    @neovim.function('TT')
    def doItPython(self, args):
        self.vim.command('echo "hello"')

    # @neovim.function('ensemble')
    # def register(self, when, audio, options=None):
    #     if when in AUTOCMDS:
    #         deco = neovim.autocmd(when)
    #         func = deco(getattr(self.orch, 'when')
    #         # autocommand registered
    #         func(audio)
    #     elif when in CUSTOMCMD:
    #         # Custom event type..
    #         raise NotImplementedError
    #     else:
    #         # TODO send error message to vim
    #         raise ValueError('Wrong command')

    @neovim.autocmd('CursorMoved')
    def cursor_moved(self):
        self.orch.cursor_moved()

    # @neovim.autocmd('CursorMovedI')
    # def cursor_movedi(self):
    #     self.orch.cursor_movedi()
