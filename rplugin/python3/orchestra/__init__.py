import neovim

import orchestra.orchestra as orch
import orchestra.util as util

@neovim.plugin
class Main(util.VimMix, object):
    def __init__(self, vim):
        # Anything called from this __in__ cannot run
        # any commands in vim, otherwise wierd errors happen!!!
        self.vim = vim
        self.orch = orch.Orchestra(vim)
        # self.ensemble(('CursorMoved', 'woosh.wav'))

    @neovim.function('Ensemble')
    def ensemble(self, args):
        '''
        Register a autocommand to an audio file,
        for each audio file you can have multiple
        parts which will automatically be added.

        e.g call Ensemble('CursorMoved', 'keys.wav')
        if keys_1 is present it will also be added.
        until keys_n+1 doesn't exist.
        starts from _1 not _0
        '''
        assert len(args) >= 2
        self.orch.ensemble(self, *args)

    @neovim.function('OrchestraSetTheme', sync=True)
    def set_theme(self, args):
        assert len(args) == 1
        theme = args[0]
        self.orch.set_theme(theme)

    @neovim.function('OrchestraAddPath', sync=True)
    def add_path(self, args):
        assert len(args) == 1
        abs_path_theme = args[0]
        self.orch.add_path(abs_path_theme)

