from ghost import Ghost
import os
import io

from ghost.bindings import QtCore

from pyBrowse.Browser import Browser, Session

class _PyBuffer(object):
    def __init__(self, buf: io.BytesIO):
        self.buf = buf

    def read(self):
        return self.buf.read()

class GhostSession(Session):
    #
    # file download
    # with open('7z1506-x64.exe', 'wb') as file:
    # file.write(eval(extra_resources[0].content)
    #
    def __init__(self, browser, gSession):
        self.browser = browser
        self.gSession = gSession
        self._updateProperties()

    def _updateProperties(self):
        self.gSession.download_images = self.download_images
        self.gSession.wait_timeout = self.timeout

    def open(self, url: str) -> (str, int):
        if url.startswith("file://"):
            file = os.path.abspath(url[7:])
            page, extra_resources = self.gSession.open("file://" + file)
        else:
            page, extra_resources = self.gSession.open(url, timeout=self.connectTimeout)
        if not page:
            self.http_status = 404
            self.content = ""
            if file and os.path.exists(file):
                #   for file mode
                self.http_status = 200
                self.content = self.gSession.content
        else:
            self.http_status = page.http_status
            self.content = page.content

        return self.content, self.http_status

    def confirm(self, confirm):
        self.gSession.confirm(confirm)

    def clearAlertMsg(self):
        self.gSession.clear_alert_message()

    def evaluate(self, script)->str:
        return self.gSession.evaluate(script)[0]

    def save_cookies(self, jar):
        pass

    def capture(self, region=None, selector=None, format=None):
        if not self.gSession.loaded:
            raise Exception("Error, page is not loaded to make capture")
        from PIL import Image
        img = self.gSession.capture(region=region, selector=selector, format=format)
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QIODevice.ReadWrite)
        img.save(buffer, "JPG")
        strio = io.BytesIO()
        strio.write(buffer.data())
        buffer.close()
        strio.seek(0)
        return Image.open(_PyBuffer(strio))

    def prompt(self, value):
        return self.gSession.prompt(value)

    def print_to_pdf(self, path, paper_size=(8.5, 11.0), paper_margins=(0, 0, 0, 0), paper_units=None, zoom_factor=1.0):
        return self.gSession.print_to_pdf(path, paper_size=paper_size, paper_margins=paper_margins, paper_units=paper_units, zoom_factor=zoom_factor)

    def waitForPageLoaded(self):
        self.gSession.wait_for_page_loaded()

    def setSize(self, x, y):
        self.gSession.set_viewport_size(x, y)

    def show(self):
        self.gSession.show()

    def sleep(self, time=0.01):
        self.gSession.sleep(time)


class GhostBrowser(Browser):
    def __init__(self):
        self._ghost = Ghost()

    def startSession(self) -> Session:
        return GhostSession(self, self._ghost.start())


# def __init__(self):
    #     #super().__init__()
