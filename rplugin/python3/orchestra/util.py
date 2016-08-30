import os
import wave
import platform
import threading
from functools import wraps
import time

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


def play_sound(file, chunk=1024):
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

    # read data (based on the chunk size)
    data = wf.readframes(chunk)
    # play stream (looping from beginning of file to the end)
    while data != '':
        # writing to the stream is what *actually* plays the sound.
        stream.write(data)
        data = wf.readframes(chunk)
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


def rate_limited(max_per_second, mode='wait', delay_first_call=False):
    """
    Decorator that make functions not be called faster than

    set mode to 'kill' to just ignore requests that are faster than the
    rate.

    set mode to 'refresh_timer' to reset the timer on successive calls

    set delay_first_call to True to delay the first call as well
    """
    lock = threading.Lock()
    min_interval = 1.0 / float(max_per_second)
    def decorate(func):
        last_time_called = [0.0]
        @wraps(func)
        def rate_limited_function(*args, **kwargs):
            def run_func():
                lock.release()
                ret = func(*args, **kwargs)
                last_time_called[0] = time.perf_counter()
                return ret
            lock.acquire()
            elapsed = time.perf_counter() - last_time_called[0]
            left_to_wait = min_interval - elapsed
            if delay_first_call:
                if left_to_wait > 0:
                    if mode == 'wait':
                        time.sleep(left_to_wait)
                        return run_func()
                    elif mode == 'kill':
                        lock.release()
                        return
                else:
                    return run_func()
            else:
                if not last_time_called[0] or elapsed > min_interval:
                    return run_func()
                elif mode == 'refresh_timer':
                    print('Ref timer')
                    lock.release()
                    last_time_called[0] += time.perf_counter()
                    return
                elif left_to_wait > 0:
                    if mode == 'wait':
                        time.sleep(left_to_wait)
                        return run_func()
                    elif mode == 'kill':
                        lock.release()
                        return
        return rate_limited_function
    return decorate

if __name__ == '__main__':
    play_sound(os.path.abspath('woosh.wav'))
    # print(get_audio_parts(['keyboard_slow.wav']))
