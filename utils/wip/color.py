def invert(color_to_convert):
    """Inverts hex color (From 00FFFF to FF0000)"""
    table = "ok".maketrans("0123456789abcdef", "fedcba9876543210")
    return "#" + color_to_convert[1:].lower().translate(table).upper()


def tbcolor_to_hex(number):
    """Converts inverted hexidemical to a normal hex color code"""
    uninverted_decimal = number - int("0xffffff", 16)
    inverted = invert(hex(uninverted_decimal).split("x")[-1])
    return inverted


def tbcolor_to_arma(number, alpha=1):
    """Converts weird tb color format to arma color code rgba with range from 0 to 1"""
    hex_input = tbcolor_to_hex(number)
    hexstrip = hex_input.lstrip("#")
    rgb = tuple(int(hexstrip[i : i + 2], 16) / 255 for i in (0, 2, 4))
    return (*rgb, alpha)


def tbcolor_to_rgb(number, alpha=255):
    """Converts weird tb color format to 255 rgba"""
    hex_input = tbcolor_to_hex(number)
    hexstrip = hex_input.lstrip("#")
    rgb = tuple(int(hexstrip[i : i + 2], 16) for i in (0, 2, 4))
    return (*rgb, alpha)
