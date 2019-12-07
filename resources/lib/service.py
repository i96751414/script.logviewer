# -*- coding: utf-8 -*-

import logging
import threading

import xbmc
import xbmcgui

from resources.lib import logviewer, utils
from resources.lib.logreader import LogReader


class Monitor(xbmc.Monitor):
    def __init__(self):
        super(Monitor, self).__init__()
        self._running = False
        self._error_popup_runner = None

    def start(self):
        self._running = True
        self.onSettingsChanged()

    def stop(self):
        self._running = False
        self._stop_error_popup_runner()

    def _start_error_popup_runner(self):
        if self._error_popup_runner is None:
            logging.info("Starting error popup runner")
            self._error_popup_runner = ErrorPopupRunner(self)
            self._error_popup_runner.start()

    def _stop_error_popup_runner(self):
        if self._error_popup_runner is not None:
            logging.info("Stopping error popup runner")
            self._error_popup_runner.stop()
            self._error_popup_runner = None

    def onSettingsChanged(self):
        if self._running:
            self._start_error_popup_runner() if utils.get_boolean("error_popup") else self._stop_error_popup_runner()


class ErrorPopupRunner(threading.Thread):
    def __init__(self, monitor):
        self._running = False
        self._monitor = monitor
        super(ErrorPopupRunner, self).__init__()

    def start(self):
        self._running = True
        super(ErrorPopupRunner, self).start()

    def run(self):
        # Start error monitor
        path = logviewer.log_location(False)
        if path is None:
            xbmcgui.Dialog().ok(utils.translate(30016), utils.translate(30017))
            return

        reader = LogReader(path)
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


def run(start_delay=20):
    monitor = Monitor()
    # Wait a few seconds for Kodi to start
    # This will also ignore initial exceptions
    if monitor.waitForAbort(start_delay):
        return
    # Start the error monitor
    monitor.start()
    # Keep service running
    monitor.waitForAbort()
    # Stop the error monitor
    monitor.stop()
