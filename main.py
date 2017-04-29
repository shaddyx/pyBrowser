import pyBrowser.GhostBrowser as browser
import time

from pyBrowser import BrowserUtils

browser = browser.GhostBrowser()
s = browser.startSession()
s.setSize(1024, 768)
s.open("http://ya.ru")
s.capture().save("1.jpg", "JPEG")
s.setValue(".input__input", "Search test")
s.capture().save("2.jpg", "JPEG")
s.click(".button_theme_websearch")
s.waitForPageUnloaded()
s.waitForPageLoaded()
s.capture().save("3.jpg", "JPEG")
count = s.selectorsCount("script")
s.markNumberedSelector("script")
s.getOuterHtml(s.genNumberedSelector(count - 1))
s.clearNumberedSelectors()
print("Count is:" + str(count))
s.sleep()

