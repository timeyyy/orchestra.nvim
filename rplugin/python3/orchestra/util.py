import os
import wave
import platform

import pyaudio

CUSTOMCMDS = (),

AUTOCMDS = (
    'BufNewFile', 'BufReadPre', 'BufRead', 'BufReadPost',
    'BufReadCmd', 'FileReadPre', 'FileReadPost', 'FileReadCmd',
    'FilterReadPre', 'FilterReadPost', 'StdinReadPre',
    'StdinReadPost', 'BufWrite', 'BufWritePre', 'BufWritePost',
    'BufWriteCmd', 'FileWritePre', 'FileWritePost',
    'FileWriteCmd', 'FileAppendPre', 'FileAppendPost',
    'FileAppendCmd', 'FilterWritePre', 'FilterWritePost',
    'BufAdd', 'BufCreate', 'BufDelete', 'BufWipeout',
    'BufFilePre', 'BufFilePost', 'BufEnter', 'BufLeave',
    'BufWinEnter', 'BufWinLeave', 'BufUnload', 'BufHidden',
    'BufNew', 'SwapExists', 'TermOpen', 'TermClose',
    'FileType', 'Syntax', 'EncodingChanged', 'TermChanged',
    'OptionSet', 'VimEnter', 'GUIEnter', 'GUIFailed',
    'TermResponse', 'QuitPre', 'VimLeavePre', 'VimLeave',
    'FileChangedShell', 'FileChangedShellPost', 'FileChangedRO',
    'ShellCmdPost', 'ShellFilterPost', 'CmdUndefined',
    'FuncUndefined', 'SpellFileMissing', 'SourcePre', 'SourceCmd',
    'VimResized', 'FocusGained', 'FocusLost', 'CursorHold',
    'CursorHoldI', 'CursorMoved', 'CursorMovedI', 'WinEnter',
    'WinLeave', 'TabEnter', 'TabLeave', 'TabNew',
    'TabNewEntered', 'TabClosed', 'CmdwinEnter', 'CmdwinLeave',
    'InsertEnter', 'InsertChange', 'InsertLeave', 'InsertCharPre',
    'TextYankPost', 'TextChanged', 'TextChangedI', 'ColorScheme',
    'RemoteReply', 'QuickFixCmdPre', 'QuickFixCmdPost',
    'SessionLoadPost', 'MenuPopup', 'CompleteDone', 'User',)


class VimMix():
    def echom(self, thing):
        self.vim.command('echom "{0}"'.format(thing))


def play_sound(file):
    '''
    chunk = length of data to read.
    '''
    if not os.path.isfile(file):
        return False

    # open the file for reading.
    wf = wave.open(file, 'rb')
    # create an audio object
    p = pyaudio.PyAudio()
    # open stream based on the wave object which has been input.
    stream = p.open(format =
                    p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)

    # read data
    data = wf.readframes(wf.getnframes())
    # play sound
    stream.write(data)

    # cleanup stuff.
    stream.close()    
    p.terminate()
    return True


def etb(func, *args, **kwargs):
    '''
    error to bool
    '''
    try:
        return func(*args, **kwargs)
    except Exception:
        return False


def get_audio_parts(file):
    '''
    see orchestra.__init__.ensemble
    '''
    def plus1(file):
        path, ext = os.path.splitext(file)
        split = path.split('_')
        old_num = etb(int, split[-1])
        if not old_num:
            split.append('1')
        else:
            split[-1] = str(old_num + 1)
        return '_'.join(split) + ext

    parts = []
    if os.path.exists(file):
        parts.append(file)
    part = plus1(file)
    while os.path.exists(part):
        parts.append(part)
        part = plus1(part)
    return parts


class InMemoryWriter(list, object):
    """
    simplify editing files
    On creation you can read all contents either from:
    an open file,
    a list
    a path/name to a file
    While iterating you can set copy=True to edit data
    as you iterate over it
    you can accesses the current position using self.i, useful if
    you are using filter or something like that while iterating
    """

    def __init__(self, file=None, copy=False):
        list.__init__(self)
        self.copy = copy
        self.data = self
        if isinstance(file, str):
            try:
                with open(file, 'r') as f:
                    self.writelines(f)
                    self.original_filename = file
            except FileNotFoundError as err:
                raise err
        elif file:
            self.writelines(file)

    def write(self, stuff):
        self.append(stuff)

    def writelines(self, passed_data):
        for item in passed_data:
            self.data.append(item)

    def __call__(self, copy=None):
        if copy:
            self.copy = True
        return self

    def __iter__(self):
        self.i = 0
        if self.copy:
            self.data_copy = self.data[:]
        return self

    def __next__(self):
        if self.i + 1 > len(self.data):
            try:
                del self.data_copy
            except AttributeError:
                pass
            raise StopIteration
        if not self.copy:
            requested = self.data[self.i]
        else:
            requested = self.data_copy[self.i]
        self.i += 1
        return requested

    def close(self):
        pass

    def readlines(self):
        return self.data

    def save(self, path=False):
        if not path:
            path = self.original_filename
        with open(path, 'w') as file:
            for row in self.data:
                file.write(row)

    def add(self, thing):
        self.write(thing+'\n')
        self.save()


def setup_logger(log_file):
    '''
    couldn't get logging module to work fml...
    just call file.add()
    '''
    if os.path.exists(log_file):
        os.remove(log_file)
    open(log_file, 'w').close()

    file = InMemoryWriter(log_file)
    file.add('System is: %s' % platform.platform())
    file.add('Python archetecture is: %s' %
                                    platform.architecture()[0])
    file.add('Machine archetecture is: %s' %
                                    platform.machine())
    return file

if __name__ == '__main__':
    play_sound(os.path.abspath('woosh.wav'))
    # print(get_audio_parts(['keyboard_slow.wav']))
