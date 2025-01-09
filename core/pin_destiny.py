from backend.lef_parser import Macro, Pin, Port, Polygon, Rect


def calculate_macro_pin_score(macro):
    """
    Calculate the pin density score for a single Macro object.
    Lower variance means better pin distribution (higher score).
    :param macro: A Macro object.
    :return: The pin density.
    """
    pin_positions = extract_pin_positions(macro)
    if not pin_positions:
        return 0  # Return full score if no signal pins
    return calculate_variance(pin_positions)


def extract_pin_positions(macro):
    """
    Extract pin positions (x coordinates) from a Macro object.
    Exclude pins with USE POWER or USE GROUND (VDD and VSS).
    :param macro: A Macro object.
    :return: A list of pin positions.
    """
    pin_positions = []
    for pin in macro.pin_dict.values():
        if pin.info.get("USE", "").upper() in ["POWER", "GROUND", "power", "ground"]:
            continue  # Skip VDD and VSS
        
        port = pin.info.get("PORT")
        if port and "LAYER" in port.info:
            pin_positions.extend(extract_positions_from_port(port))
    return pin_positions


def extract_positions_from_port(port):
    """
    Extract pin positions from a PORT object.
    :param port: A PORT object.
    :return: A list of pin positions.
    """
    positions = []
    for layer in port.info["LAYER"]:
        for shape in layer.shapes:
            if shape.type == "RECT":
                positions.append(calculate_rect_center(shape))
            elif shape.type == "POLYGON":
                positions.append(calculate_polygon_center(shape))
    return positions


def calculate_rect_center(rect):
    """
    Calculate the center x coordinate of a RECT.
    :param rect: A Rect object.
    :return: The center x coordinate.
    """
    x0, x1 = rect.points[0][0], rect.points[1][0]
    return (x0 + x1) / 2


def calculate_polygon_center(polygon):
    """
    Calculate the center x coordinate of a POLYGON.
    :param polygon: A Polygon object.
    :return: The center x coordinate.
    """
    x_coords = [point[0] for point in polygon.points]
    return sum(x_coords) / len(x_coords)


def calculate_variance(pin_positions):
    """
    Calculate the variance of pin positions.
    :param pin_positions: A list of pin positions.
    :return: The variance.
    """
    mean = sum(pin_positions) / len(pin_positions)
    return sum((x - mean) ** 2 for x in pin_positions) / len(pin_positions)

def calc_pin_density(all_macros, macro_name=None):
    """
    Calculate the pin density for one or all macros in the LEF file.
    Pin density is calculated as the variance of pin positions.
    Lower variance means better pin distribution (higher score).
    :param all_macros: A dictionary of all Macro objects.
    :param macro_name: The name of a specific macro to calculate. If None, calculate for all macros.
    :return: A dictionary with macro names as keys and pin density scores as values.
             If macro_name is specified, return a single score.
    """
    if macro_name:
        if macro_name not in all_macros:
            raise ValueError(f"Macro '{macro_name}' not found in the provided macros.")
        return {macro_name: calculate_macro_pin_score(all_macros[macro_name])}
    return {name: calculate_macro_pin_score(macro) for name, macro in all_macros.items()}
