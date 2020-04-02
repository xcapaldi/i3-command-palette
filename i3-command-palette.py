import argparse
import subprocess
from pathlib import Path

def set_mod(keybind, mod):
    """Define how the mod key should be displayed."""
    # check for the rare keyboard specific keybinding
    if '+' in keybind:
        # this could be done simply using the set number of characters but I am trying to make it generic
        split_keys = keybind.split('+')
        new_keybind = mod
        for i in split_keys[1:]:
            new_keybind += '+'
            new_keybind += i
        return new_keybind
    # otherwise it's a keyboard binding
    else:
        return keybind

def create_palette(path, mod_var="$mod", mod=None):
    """Create a dictionary defining the command palette."""
    # initialize dictionary to contain description, keybinding and command
    # format will be description:(keybinding, command)
    palette = {}
    # initialize dictionary to contain variables
    variables = {}
    # initialize flag to false
    flag = False
    
    with open(path) as f:
        for line in f:
            # we need to save the keybinding and command
            if flag:
                # check if there is a keybinding
                if line[0:7] == 'bindsym':
                    # in this case, need to separate keybinding from command
                    split_line = line.split(' ')
                    # change how the mod key is displayed if desired
                    if mod != None:
                        keybind = set_mod(split_line[1], mod)
                    else:
                        keybind = split_line[1]
                    command = ''
                    for i in split_line[2:]:
                        command += i
                        command += ' '
                    # remove the excess space and newline character
                    command = command[:-2]
                # otherwise there must be no keybinding
                else:
                    keybind = None
                    command = line[2:-1]
                # add to palette
                palette[description]=(keybind, command)
                # and reset flag
                flag = False
            elif "# description:" in line:
                description = line[15:-1]
                flag = True
            # check if we have an i3 variable
            elif line[0:4] == "set ":
                var = line.split(' ')[1]
                val = line[line.index(var) + len(var) + 1:-1]
                # $mod and $mode_... will conflict so we remove $mod
                if var != mod_var:
                    variables[var] = val
            # now update palette so the commands will work with i3-msg
            # this is done by substituting the variables on the command side
            for desc in palette:
                # check against each variable
                for var in variables:
                    # if present replace
                    if var in palette[desc][1]:
                        palette[desc] = (palette[desc][0], palette[desc][1].replace(var, variables[var]))
    return palette

def palette_out(palette, show_bind=True):
    """Convert palette dictionary to output for dmenu or rofi."""
    output = ""
    for key in palette:
        # check if we want to show the keybindings
        if show_bind:
            output += str(palette[key][0]) + ' -> ' + key + '\n'
        else:
            output += key + '\n'
    return output

def get_selection(choices, selector="dmenu", prompt="command palette"):
    """Get command selection from user using dmenu or rofi."""
    choices = subprocess.Popen(('echo', choices), stdout=subprocess.PIPE)
    # change output based on selector
    if selector=="rofi":
        output = subprocess.check_output(('rofi', '-dmenu', '-p', prompt), stdin=choices.stdout)
    else:
        output = subprocess.check_output(('dmenu', '-p', prompt), stdin=choices.stdout)
    # now only return description
    description = str(output).split(' -> ')[-1][:-3]
    return str(description)

def run_command(description, palette):
    """Reference the command palette to run the command associated with description."""
    print('i3-msg' +  ' "' + palette[description][1] + '"')
    #print(palette)
    subprocess.call(('i3-msg', palette[description][1]))
    return

# get home path
home = str(Path.home())
# path to the i3 configuration file
path = home + "/.config/i3/config"

# parse commandline input
parser = argparse.ArgumentParser(description="parse i3 configuration to generate list of commands or run a command palette")
parser.add_argument("-c", "--config", nargs='?', default=path, type=str, help="path to i3 config")
parser.add_argument("-v", "--var", nargs='?', default="$mod", type=str, help="variable used for modifier in configuration")
parser.add_argument("-m", "--mod", nargs='?', default=None, type=str, help="replace modifier variable with string or character")
parser.add_argument("-r", "--rofi", help="use rofi as the selection mechanism", action="store_true")
parser.add_argument("-p", "--prompt", nargs='?', default="command palette", type=str, help="prompt for dmenu or rofi")
parser.add_argument("-l", "--list", help="print list of commands", action="store_true")
parser.add_argument("-b", "--bind", help="hide associated keybinding", action="store_false")

args = parser.parse_args()

# create the palette
palette = create_palette(args.config, args.var, args.mod)

if args.rofi:
    select_mech = 'rofi'
else:
    select_mech = 'dmenu'

# just print cheatsheet of commands
if args.list:
    print(palette_out(palette, show_bind=args.bind))
# otherwise we want a command palette
else:
    run_command(get_selection(palette_out(palette, show_bind=args.bind), selector=select_mech, prompt=args.prompt), palette)
