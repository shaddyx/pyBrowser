import unittest
import os
import time
from pyBrowse.GhostBrowser import GhostBrowser


class TestGhostBrowser(unittest.TestCase):
    def createBrowser(self):
        return GhostBrowser()
    cache = {}
    def _open(self, url):
        if url not in self.cache:
            session = self.createBrowser().startSession()
            a, b = session.open(url)
            self.cache[url] = (a, b, session)
        return self.cache[url][0], self.cache[url][1], self.cache[url][2]

    def test_Open(self):
        res, httpState, session = self._open("file://test/files/doc.html")
        self.assertEqual(httpState, 200)

    def test_find(self):
        res, httpState, session = self._open("file://test/files/doc.html")
        self.assertEqual(httpState, 200)
        self.assertTrue(session.exists("body"))
        self.assertTrue(session.exists(".wy-grid-for-nav"))
        self.assertFalse(session.exists(".highlightrrrr"))
        self.assertEqual(session.getText("title"), "ghost.py — Ghost.py 0.2.2 documentation")

        b = session.getRegion("body")

        self.assertEqual(b.width, 625)
        self.assertEqual(b.height, 480)

    def test_checkGlobalExists(self):
        res, httpState, session = self._open("file://test/files/doc.html")
        self.assertEqual(httpState, 200)
        self.assertTrue(session.globalExists("$u"))
        self.assertFalse(session.globalExists("$uttts"))

    def test_SaveToPdf(self):
        res, httpState, session = self._open("file://test/files/doc.html")
        self.assertEqual(httpState, 200)
        session.print_to_pdf("./1.pdf")
        self.assertTrue(os.path.exists("./1.pdf"))
        os.remove("./1.pdf")



