import sys
import xbmc
import xbmcgui
import logviewer
from utils import *


def has_addon(addon_id):
    return xbmc.getCondVisibility("System.HasAddon(%s)" % addon_id) == 1


def get_opts():
    headings = []
    handlers = []

    # Show log
    headings.append(translate(30001))
    handlers.append(show_log)

    # Show old log
    headings.append(translate(30002))
    handlers.append(show_old_log)

    # Upload log
    if has_addon("script.kodi.loguploader"):
        headings.append(translate(30015))
        handlers.append(upload_log)

    # Open Settings
    headings.append(translate(30011))
    handlers.append(open_settings)

    return headings, handlers


def show_log():
    content = logviewer.get_content(False, get_inverted(), get_lines(), True)
    logviewer.window(ADDON_NAME, content, default=is_default_window())


def show_old_log():
    content = logviewer.get_content(True, get_inverted(), get_lines(), True)
    logviewer.window(ADDON_NAME, content, default=is_default_window())


def upload_log():
    xbmc.executebuiltin("RunScript(script.kodi.loguploader)")


def run():
    if len(sys.argv) > 1:
        '''
        Integration patterns below:
        Eg: xbmc.executebuiltin("RunScript(script.logviewer, show_log)")
        '''
        method = sys.argv[1]

        if method == "show_log":
            show_log()
        elif method == "show_old_log":
            show_old_log()
        else:
            e = "Method %s does not exist" % method
            raise NotImplementedError(e)
    else:
        headings, handlers = get_opts()
        index = xbmcgui.Dialog().select(ADDON_NAME, headings)
        if index >= 0:
            handlers[index]()
