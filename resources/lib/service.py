import xbmc
import time
import utils
import threading
import logviewer


class LazyMonitor(xbmc.Monitor):
    def __init__(self):
        xbmc.Monitor.__init__(self)
        self._runner = None

    def start(self):
        # Assure the runner is stopped
        self.stop()
        # Start the runner
        self._runner = Runner()
        self._runner.start()

    def stop(self):
        if self._runner is not None:
            self._runner.stop()
            self._runner = None

    def onSettingsChanged(self):
        self.start()


class Runner(threading.Thread):
    def __init__(self):
        self.running = False
        threading.Thread.__init__(self)

    def start(self):
        self.running = True
        threading.Thread.start(self)

    def run(self):
        if utils.get_setting("error_popup") == "true":
            # Start error monitor
            log_location = logviewer.log_location(False)
            reader = logviewer.LogReader(log_location)

            # Ignore initial errors
            reader.tail()

            while not xbmc.abortRequested and self.running:
                content = reader.tail()
                parsed_errors = logviewer.parse_errors(content, set_style=True)
                if parsed_errors:
                    logviewer.window(utils.ADDON_NAME, parsed_errors, default=utils.is_default_window())
                xbmc.sleep(500)

    def stop(self):
        self.running = False
        # Wait for thread to stop
        self.join()


def run(delay=20):
    # Wait a few seconds for Kodi to start
    initial_time = time.time()
    while time.time() - initial_time < delay:
        # Check for abort requested
        if xbmc.abortRequested:
            return
        xbmc.sleep(500)

    # Start the error monitor
    monitor = LazyMonitor()
    monitor.start()

    # Keep service running
    while not xbmc.abortRequested:
        xbmc.sleep(500)

    # Stop the error monitor
    monitor.stop()
