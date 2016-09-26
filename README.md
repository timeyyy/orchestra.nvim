# Orchestra.nvim
### Add another dimension to your coding experience

- [Introduction](#introduction)
- [Installing](#installing)
    - [Dependencies](#dependencies)
- [Usage](#usage)
    - [Plug and Play](#plugandplay)
    - [Configuring](#configuring)
- [Development](#development)

__Status = ALPHA i.e api may change/improve__

#### News

 * [Distorition and delay](https://github.com/timeyyy/orchestra.nvim/pull/2) fixed. Many thanks IndicaInkwell!


## <a id="introduction"></a>Introduction

Orchestra.nvim is a plugin for neovim that lets you bind sound effects
to different actions.  The motivation was mostly for fun but it seems 
useful for training good vim habits. You can literally hear unproductivity
and when/where you could improve.


## <a id="installing"></a>Installing

I use dein.vim

```VimL
call dein#add('timeyyy/orchestra.nvim')
```

Then run 
```VimL
call dein#install()
UpdateRemotePlugins
```


### <a id="dependencies"></a>Dependencies 
 * python3
 * the neovim client for python - `pip install neovim`
 * pyaudio - [install instructions](http://people.csail.mit.edu/hubert/pyaudio/)


## <a id="usage"></a>Usage

We have some rudimentary theme (tune) support

```VimL
call dein#add('timeyyy/clacklack.symphony')

call orchestra#prelude()
call orchestra#set_tune('clackclack')
```

[List of Themes](https://github.com/timeyyy/orchestra.nvim/wiki/Themes)


### <a id="configuring"></a>Configuring

Themes are just normal vim plugins with a few requirements.

e.g theme "bumblebee\_flight": 

    autoload/
        bumblebee_flight.vim             - the main file
        buzz.wav                          - audio file
        flap.wav 
        flap_1.wav 
        flap_2.wav 

bublebee\_flight.vim:

```VimL
" Absolute path of script file with symbolic links resolved:
let s:current_file = resolve(expand('<sfile>:p'))
call OrchestraAddPath(s:current_file)
```

We can now customize the behavior of our script.  For the moment we only have `Ostinato` which is just autocmds.

```VimL
call Ostinato('CursorMovedI', 'flap.wav')
call Ostinato('CursorMoved', 'buzz.wav')
```

If you just don't want to install a theme you can call `Ostinato` from within your vimrc as long as it is after `orchestra#prelude()`

The Ostinato can handle multiple audio files.
Multiple parts suffixed with : \_# will automatically be discovered and played back at random.


## <a id="development"></a>Development

Guidance and or pull requests welcome.

#### Plans

* Allow binding to specific keys 
* Custom Events, i.e bind to a range of chars being deleted/inserted
* More themes
* Figure out why 80% Autcommands are not procing..
* Ability to squelch/prioritize simultaneous events
* Introspection functions i.e see what is registerd
* Unregister Function

