# -*- coding: utf-8 -*-

import logging
import sys

import xbmc
import xbmcaddon

PY3 = sys.version_info.major >= 3

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo("path")
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_ID = ADDON.getAddonInfo("id")

if PY3:
    def translate(text):
        return ADDON.getLocalizedString(text)

    def encode(s):
        return s.encode("utf-8")

    def decode(s):
        return s.decode("utf-8")
else:
    ADDON_PATH = ADDON_PATH.decode("utf-8")

    def translate(text):
        return ADDON.getLocalizedString(text).encode("utf-8")

    def encode(s):
        return s

    def decode(s):
        return s


def get_setting(setting):
    return ADDON.getSetting(setting)


def get_boolean(setting):
    return get_setting(setting) == "true"


def open_settings():
    ADDON.openSettings()


def get_inverted():
    return get_boolean("invert")


def get_lines():
    nr_lines = get_setting("lines")
    if nr_lines == "1":
        return 100
    elif nr_lines == "2":
        return 50
    elif nr_lines == "3":
        return 20
    else:
        return 0


def is_default_window():
    return not get_boolean("custom_window")


def parse_exceptions_only():
    return get_boolean("exceptions_only")


class KodiLogHandler(logging.StreamHandler):
    levels = {
        logging.CRITICAL: xbmc.LOGFATAL,
        logging.ERROR: xbmc.LOGERROR,
        logging.WARNING: xbmc.LOGWARNING,
        logging.INFO: xbmc.LOGINFO,
        logging.DEBUG: xbmc.LOGDEBUG,
        logging.NOTSET: xbmc.LOGNONE,
    }

    def __init__(self):
        super(KodiLogHandler, self).__init__()
        self.setFormatter(logging.Formatter("[{}] %(name)s: %(message)s".format(ADDON_ID)))

    def emit(self, record):
        xbmc.log(self.format(record), self.levels[record.levelno])

    def flush(self):
        pass


def set_logger(name=None, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.addHandler(KodiLogHandler())
    logger.setLevel(level)
