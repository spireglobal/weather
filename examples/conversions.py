from math import atan2, pi, sqrt


def wind_speed_from_u_v(u, v):
    return sqrt(pow(u, 2) + pow(v, 2))


def wind_direction_from_u_v(u, v):
    """
    Meteorological wind direction
      90° corresponds to wind from east,
      180° from south
      270° from west
      360° wind from north.
      0° is used for no wind.
    """
    if (u, v) == (0.0, 0.0):
        return 0.0
    else:
        return (180.0 / pi) * atan2(u, v) + 180.0
