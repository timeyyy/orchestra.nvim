import os
import wave

import pyaudio


class VimMix():
    def echom(self, thing):
        self.vim.command('echom "{0}"'.format(thing))


def play_sound(file, chunk=1024):
    '''
    chunk = length of data to read.
    '''
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





if __name__ == '__main__':
    import os
    play_sound(os.path.abspath('woosh.wav'))
    print(os.getcwd())
    print(get_audio_parts(['keyboard_slow.wav']))
