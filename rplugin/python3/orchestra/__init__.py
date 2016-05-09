import os
import neovim

import orchestra.orchestra as orch
import orchestra.util as util

@neovim.plugin
class Main(util.VimMix, object):
    def __init__(self, vim):
        # Anything called from this __in__ cannot run
        # any commands in vim, otherwise wierd errors happen!!!
        self.vim = vim
        self.DEBUG = False
        self.orch = orch.Orchestra(vim, main=self)
        self.orch.DEBUG = self.DEBUG
        self.setup_functions()
        if self.DEBUG:
            self.logger = util.setup_logger('orchestra.log')

    @neovim.function('Ostinato')
    def ostinato(self, args):
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
        self.orch.ostinato(*args)

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

    def setup_functions(self):
        '''
        For the moment neovim handlers for functions
        only get checked at startup.
        We define a bunch of functions so autocommands
        can we registered to them.
        '''
        # TODO Remove this when neovim updates
        for event in orch.AUTOCMDS:
            func_name = 'Orchestra_' + event
            @neovim.function(func_name)
            def func(nvim, audio):
                self.orch.queue_audio(audio)
            setattr(self, func_name, func)

