"""
Funciones auxiliares para ayudar en la conversión de fechas
"""

__author__ = "María Andrea Vignau"

import datetime
import pytz   # fades pytz

local_tz = None
local_date_format = None

def set_locale(locale, date_format):
    global local_tz, local_date_format
    local_tz = pytz.timezone(locale)
    local_date_format = date_format.replace("@", "%")

def localize_date(dt_obj):
    """Toma una fecha localizada en UTC y la devuelve convertida a la hora local."""
    dt_obj = pytz.utc.localize(dt_obj).astimezone(local_tz)
    return dt_obj.strftime(local_date_format)


def fromtimestamp(timestamp):
    """Toma una fecha en formato timestamp y la devuelve convertida a la hora local."""
    dt_obj = datetime.datetime.fromtimestamp(timestamp)
    return localize_date(dt_obj)


def fromdatestr(date_str):
    """Toma una fecha en formato string ISO y la devuelve convertida a la hora local."""
    dt_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    return localize_date(dt_obj)
