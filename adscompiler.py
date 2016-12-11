import sys

# Script vars
ads_data = []
ads_consts = []

# Compiler vars
labels = {}
jumps = {}

# System vars
sysvars = {
    "caps": 0,
    "num": 1,
    "scroll": 2
}

# Keycodes
keyCodes = {
    " ":        "KEY_SPACE",

    "enter":    "KEY_ENTER",
    "space":    "KEY_SPACE",

    "ctrl":     "KEY_LEFT_CTRL",
    "shift":    "KEY_LEFT_SHIFT",
    "alt":      "KEY_LEFT_ALT",
    "gui":      "KEY_LEFT_GUI",

    "right":    "KEY_RIGHT_ARROW",
    "left":     "KEY_LEFT_ARROW",
    "down":     "KEY_DOWN_ARROW",
    "up":       "KEY_UP_ARROW",

    "esc":      "KEY_ESC",
    "back":     "KEY_BACKSPACE",
    "tab":      "KEY_TAB",

    "ins":      "KEY_INSERT",
    "home":     "KEY_HOME",
    "pgup":     "KEY_PAGE_UP",
    "del":      "KEY_DELETE",
    "end":      "KEY_END",
    "pgdn":     "KEY_PAGE_DOWN",

    "caps":     "KEY_CAPS_LOCK",

    "f1":       "KEY_F1",
    "f2":       "KEY_F2",
    "f3":       "KEY_F3",
    "f4":       "KEY_F4",
    "f5":       "KEY_F5",
    "f6":       "KEY_F6",
    "f7":       "KEY_F7",
    "f8":       "KEY_F8",
    "f9":       "KEY_F9",
    "f10":      "KEY_F10",
    "f11":      "KEY_F11",
    "f12":      "KEY_F12"
}

# Functions
def keyCode(key, warn = False):
    if key in keyCodes:
        return keyCodes[key]

    elif (key >= 'A' and key <= 'Z') or\
        (key >= 'a' and key <= 'z') or\
        (key >= '0' and key <= '9'):
            return "KEY_" + key.upper()

    else:
        if warn:
            print("]]] WARNING: Unknown key '" + key + "'")

        return 0

def pushConst(num):
    # Push number into constants if it doesn't exist already
    if not num in ads_consts:
        ads_consts.append(num)

    idx = ads_consts.index(num)
    if idx > 255:
        print("ERROR: Too many constants!")
        exit()

    return idx

# Check args
if len(sys.argv) != 2:
    print("Usage: adscompiler.py <script>")
    exit()

# Open ardoducky script
inf = open(sys.argv[1], "r")

# Read lines
for line in inf:
    # Remove newlines
    line = line.replace("\n", "").replace("\r", "")

    # Line too short?
    if len(line) < 1:
        continue

    # Split
    f = line.find(' ')
    if f < 0:
        cmd = line
        arg = ""
    else:
        cmd = line[:f]
        arg = line[f + 1:]

    # Write string
    if cmd == "write":
        for c in arg:
            kc = keyCode(c)
            if kc == 0:
                ads_data.append(5) # Alt code
                ads_data.append("'" + c.replace('\\', '\\\\') + "'")
            else:
                # If uppercase
                if c != c.lower():
                    ads_data.append(3) # Hold
                    ads_data.append(keyCode("shift", True))

                ads_data.append(1) # Press key
                ads_data.append(kc)

                # If uppercase
                if c != c.lower():
                    ads_data.append(4) # Release
                    ads_data.append(keyCode("shift", True))

    # Wait
    elif cmd == "wait":
        # Push command
        ads_data.append(2) # Wait
        ads_data.append(pushConst(int(arg))) # Const index

    # Press key
    elif cmd == "press":
        keys = arg.split('+')
        for key in keys[:-1]:
            ads_data.append(3) # Hold key
            ads_data.append(keyCode(key, True)) # Keycode

        ads_data.append(1) # Press key
        ads_data.append(keyCode(keys[-1], True)) # Keycode

        for key in reversed(keys[:-1]):
            ads_data.append(4) # Release key
            ads_data.append(keyCode(key, True)) # Keycode

    # Label
    elif cmd[0] == ':':
        lbl = cmd[1:]
        if lbl in labels:
            print("ERROR: Label '" + lbl + "' already exists!")
            exit()

        labels[lbl] = len(ads_data)

    # Goto label
    elif cmd == "goto":
        # Don't put in the real jump. We're not sure the label exist yet.
        ads_data.append(6) # Jump
        jumps[len(ads_data)] = arg
        ads_data.append(0) # Dummy target

    # Jump if sysvar is true
    elif cmd == "ifj":
        args = arg.split(' ');
        var = args[0]
        lbl = args[1]

        if var[0] != "$":
            print("ERROR: '" + var + "' is not a valid variable!")
            exit()

        if not var[1:] in sysvars:
            print("ERROR: Sysvar '" + var[1:] + "' not found!")
            exit()

        ads_data.append(7) # Jump if sysvar true
        ads_data.append(sysvars[var[1:]])

        # Don't put in the real jump. We're not sure the label exist yet.
        jumps[len(ads_data)] = lbl
        ads_data.append(0) # Dummy target

    # Unknown
    elif cmd != '#':
        print("]]] WARNING: Unhandled command '" + cmd + "'")

# Close input file
inf.close()

# Handle jumps
for i in jumps:
    if not jumps[i] in labels:
        print("ERROR: Label '" + jumps[i] + "' doesn't exist!")
        exit()

    ads_data[i] = pushConst(labels[jumps[i]])

# Turn data into strings
for i in range(len(ads_data)):
    ads_data[i] = str(ads_data[i])

for i in range(len(ads_consts)):
    ads_consts[i] = str(ads_consts[i])

# Create header
outsrc =  "#include <avr/pgmspace.h>\n\n";
outsrc += "const uint8_t ads_data[] PROGMEM = { " + ", ".join(ads_data) +  " };\n"
outsrc += "const int ads_len = " + str(len(ads_data)) + ";\n"
outsrc += "const int ads_consts[] = { " + ", ".join(ads_consts) + " };\n"

# Write file
outf = open("script.h", "w")
outf.write(outsrc)
outf.close()

# Success!
print("Wrote to 'script.h' successfully!")
