import neovim

import orchestra.orchestra as orch
import orchestra.util as util

@neovim.plugin
class Main(util.VimMix, object):
    def __init__(self, vim):
        self.vim = vim
        self.orch = orch.Orchestra(vim)
        self.ensemble(('CursorMovedI', 'keyboard_slow.wav'))

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
        when, *audio = args
        audio = util.get_audio_parts(audio)
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
