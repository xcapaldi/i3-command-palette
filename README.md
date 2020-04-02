# i3-command-palette
Parse i3 configuration to generate list of commands or run a command palette.

![Generated cheatsheet](cheatsheet.png?raw=true "Generated cheatsheet")↩

## Philosophy

The desktop environment serves as an interface between the user (you) and the task you're trying to perform.
The efficacy of a window manager can be gauged by how little friction it induces between the user and their tasks.
Tiling window managers, like i3wm already remove the need to manually position windows or use the mouse in most cases.
i3wm in particular adds a modal interface which reduces the number of keybindings the user needs to memorize.
Nonetheless, I find on my own system I still need to remember bindings to enter modes for managing the system session, volume, window layout, colorscheme, window size, marks, screenshots, mail clients and video viewers.
This is in additional to the default mode bindings for navigation, floating, maximizing and launching quick terminal applications like my calculator.
I find that most of these bindings are used infrequently and I rarely remember them when I need them.
Instead I like the interface in Emacs where you can always use M-x to run a command by name.
I know Sublime Text also implemented something similar with its command palette.
This python script attempts to do the same with the i3 configuration.
It has no dependencies beyond python itself and I've found that it runs very quickly as is.
In the future, if speed becomes an issue, I can implement pickling the dictionary of commands after parsing the config to save time.
## Inspiration

This was directly inspired by Phate6660's [sxhkd-bindings](https://github.com/Phate6660/sxhkd-bindings).
I highly recommend checking it out.
He achieves somewhat similar functionality for sxhkd with a minimal shell script.

## Usage

```
usage: i3-command-palette.py [-h] [-c [CONFIG]] [-v [VAR]] [-m [MOD]] [-r]
                             [-p [PROMPT]] [-l] [-b]

parse i3 configuration to generate list of commands or run a command palette

optional arguments:
  -h, --help            show this help message and exit
  -c [CONFIG], --config [CONFIG]
                        path to i3 config
  -v [VAR], --var [VAR]
                        variable used for modifier in configuration
  -m [MOD], --mod [MOD]
                        replace modifier variable with string or character
  -r, --rofi            use rofi as the selection mechanism
  -p [PROMPT], --prompt [PROMPT]
                        prompt for dmenu or rofi
  -l, --list            print list of commands
  -b, --bind            hide associated keybinding
```

I recommend binding this python script to something simple in your i3 configuration.
Here is my keybinding but $mod+Shift+Return would also be a good option:

```
bindsym $mod+space exec python ~/checkout/i3-command-palette/i3-command-palette.py -r -m 🚀
```

### -c, [CONFIG], --config [CONFIG]

By default, the script will read the config file at $HOME/.config/i3/config.
You can set an alternative path with the -c flag.

### -v, [VAR], --var

Typically the principle modifier key is set with a variable in the i3 configuration:

```
set $mod Mod4
```

By default, the script assumes this variable is $mod but you can change it with with -v flag.

### -m [MOD], --mod

You can replace the modifier variables mentioned above with another string or character of your choosing.
If you're using rofi feel free to use emojis (👑, 🥣, 🚀!) but be aware that in unpatched dmenu they won't display properly.

### -r, --rofi

By default, the script will use dmenu as its selection mechanism.
If you prefer you can set it to rofi with the -r flag.

### -p [PROMPT], --prompt [PROMPT]

The default prompt for rofi and dmenu is command palette:
You can change it to another string with this flag.

### -l, --list

Using this flag will output a complete list of your keybinding (and unbound commands) to the terminal.
It works with the -c, -m and -b flags.
It is useful if you would like to print a cheatsheet, quickly share your bindings with someone else or bind a key to display on onscreen cheatsheet.

### -b, --bind

By default the script will always display the associated keybinding with a command.
This is useful if you want to use it as a memory aid.
If you're only using the command palette as a launcher and you don't want to remember your keybindings (or don't use keybindings at all), you can use the -b flag to remove the binding information from the output.

## Configuration format

This script requires your i3 configuration file to be in a particular format.

### Defining variables using set

Only use a single space between the components of this line.

```
set $term kitty
```

This can result in a slightly more messy configuration because you cannot line up your variables 
Do this:

```
set $left h
set $down j
set $up k
set $right l
```

Don't do this:

```
set $left  h
set $down  j
set $up    k
set $right l
```

For mode name variables it should look something like this:

```
set $mode_resize "RESIZE [h] -width [l] +width [j] -height [k] +height"
```

### Defining keybindings

All keybindings need a description on the previous line in a particular format:

```
# description: kill focused window
bindsym $mod+Shift+q kill
```

This is the beginning of the description line: "# description: "
Anything following that will be presented as the command description when running the script.
If you want to omit a keybinding from the output, simply don't add a description line above it.

#### Do NOT add descriptions within your modes!

If you want to access commands from within a defined mode, use the defining unbound command format below.

### Defining commands that are not bound

You can also add commands to command palette that are not bound in your configuration.
To do this, use the same description line above the command.
Then simple use this format for the command itself: "# command-to-run"

Simple example:

```
# description: restart i3 session inplace
# restart
```

Complex example:

```
# description: exit i3
# exec i3-nagbar -t warning -m 'Really exit i3? This will end X session.' -B 'Yes, exit i3' 'i3-msg exit'
```

## Future work

### Variables in keybindings

Variables defined in the keybindings themselves like $left for h are not substituted in the output.
I doubt this will be an issue for any use case but if it is, the script could be modified to do that.

### Error checking

As of now, I don't set any sort error checking or useful error messages.
The script runs well with my configuration but I should implement a more robust system.

### Pickling commands

Each time you run the script, it will parse your entire i3 configuration and produce a dictionary of descriptions, commands and keybindings.
This works very quickly on my system but if performance is an issue for you, I can modify the script so that it only parses the configuration once and pickles the resulting dictionary for quick lookups.

