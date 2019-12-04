# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import threading

from resources.lib import logviewer, utils


class Monitor(xbmc.Monitor):
    def __init__(self):
        xbmc.Monitor.__init__(self)
        self._runner = None

    def start(self):
        if self._runner is None:
            self._runner = Runner(self)
            self._runner.start()

    def stop(self):
        if self._runner is not None:
            self._runner.stop()
            self._runner = None

    def restart(self):
        self.stop()
        self.start()

    def onSettingsChanged(self):
        self.restart()


class Runner(threading.Thread):
    def __init__(self, monitor):
        self._running = False
        self._monitor = monitor
        threading.Thread.__init__(self)

    def start(self):
        self._running = True
        threading.Thread.start(self)

    def run(self):
        if utils.get_setting("error_popup") == "true":
            # Start error monitor
            path = logviewer.log_location(False)
            if path is None:
                xbmcgui.Dialog().ok(utils.translate(30016), utils.translate(30017))
                return

            reader = logviewer.LogReader(path)
            exceptions = utils.parse_exceptions_only()

            # Ignore initial errors
            reader.tail()

            while not self._monitor.abortRequested() and self._running:
                content = reader.tail()
                parsed_errors = logviewer.parse_errors(content, set_style=True, exceptions_only=exceptions)
                if parsed_errors:
                    logviewer.window(utils.ADDON_NAME, parsed_errors, default=utils.is_default_window())
                self._monitor.waitForAbort(1)

    def stop(self):
        self._running = False
        # Wait for thread to stop
        self.join()


def run(delay=20):
    monitor = Monitor()
    # Wait a few seconds for Kodi to start
    if monitor.waitForAbort(delay):
        return

    # Start the error monitor
    monitor.start()

    # Keep service running
    monitor.waitForAbort()

    # Stop the error monitor
    monitor.stop()
