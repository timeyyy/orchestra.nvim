
import neovim

import orchestra.orchestra as orch
import orchestra.util as util

@neovim.plugin
class Main(util.VimMix, object):
    def __init__(self, vim):
        self.vim = vim
        self.orch = orch.Orchestra(vim)
        # self.ensemble('CursorMoved', 'woosh.wav')

    @neovim.function('Ensemble')
    def ensemble(self, args):
        assert len(args) <= 2
        when, audio = args
        if when in orch.AUTOCMDS:
            @neovim.autocmd(when)
            def func(nvim):
                self.orch.queue_audio(audio)
            setattr(self, '_'+when, func)
        elif when in orch.CUSTOMCMDS:
            # Custom event type..
            raise NotImplementedError
        else:
            # TODO send error message to vim
            raise ValueError('Wrong command')
