BRONZE = "#cd7f32"
SILVER = "#c0c0c0"
GOLD = "#ffd700"
PLATINUM = "#e5e4e2"

RED = "#ff0000"
ORANGE = "#ffa500"
GREEN = "#50c878"
GREY = "#808080"
LIGHT_BLUE = "#03cffc"
BLACK = "#000000"
WHITE = "#ffffff"

DEFAULT_BACKGROUND = "#0084ff"

CLOCK_COLOURS = []
for red in range(256):
    CLOCK_COLOURS.append(f"#{hex(red)[2:].zfill(2)}ff00")
for green in range(254, -1, -1):
    CLOCK_COLOURS.append(f"#ff{hex(green)[2:].zfill(2)}00")