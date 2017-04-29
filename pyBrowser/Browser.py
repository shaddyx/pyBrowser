from abc import ABCMeta, abstractmethod, abstractproperty
import codecs
import time

def _randStr():
    import uuid
    return "_" + str(uuid.uuid4()).replace("-","")

class SelectorException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Region(object):
    x = 0
    y = 0
    width = 0
    height = 0
    def __init__(self, str):
        self.x, self.y, self.width, self.height = map(lambda x: int(x), str.split(":"))

    def __str__(self):
        return "Region[x={self.x}, y={self.y}, width={self.width}, height={self.height}]".format(self=self)


#
#   Selector to query nth: div:nth-of-type(4)
#

class Session(object):
    """represents browser tab"""
    http_status = 0
    content = 0
    timeout = 20
    connectTimeout = 20
    download_images = False
    _numberSelector = _randStr()

    @abstractmethod
    def open(self, url)-> (str, int):
        """opens url"""

    @abstractmethod
    def confirm(self, confirm):
        """confirms alert"""
        pass

    @abstractmethod
    def capture(self, region=None, selector=None, format=None):
        pass

    @abstractmethod
    def clearAlertMsg(self):
        """clears alert message on page"""
        pass

    @abstractmethod
    def evaluate(self, script: str) -> str:
        """Evaluates script on page and returns javascript result
        For sample evaluate("12345") will return 12345
        """
        pass

    @abstractmethod
    def prompt(self, value):
        """enters value to prompt"""
        pass

    @abstractmethod
    def save_cookies(self, jar):
        pass

    @abstractmethod
    def waitForPageLoaded(self):
        """waits until page loads"""
        pass

    @abstractmethod
    def setSize(self, x, y):
        """sets viewport size"""
        pass

    @abstractmethod
    def show(self):
        """shows browser"""
        pass

    @abstractmethod
    def sleep(self, time=0.01):
        pass

    @abstractmethod
    def print_to_pdf(
            self,
            path,
            paper_size=(8.5, 11.0),
            paper_margins=(0, 0, 0, 0),
            paper_units=None,
            zoom_factor=1.0,
    ):
        """prints page to pdf"""
        pass

    def exists(self, selector: str) -> bool:
        """Checks if element exists for given selector"""
        return self.evaluate("""document.querySelector('%s') != null""" % (selector))

    def evaluate_js_file(self, path, encoding='utf-8', **kwargs):
        """Evaluates javascript file at given path in current frame.
        Raises native IOException in case of invalid file.
        :param path: The path of the file.
        :param encoding: The file's encoding.
        """
        with codecs.open(path, encoding=encoding) as f:
            return self.evaluate(f.read(), **kwargs)

    def globalExists(self, global_name):
        """Checks if javascript global exists.
        :param global_name: The name of the global.
        """
        return self.evaluate(
            '!(typeof this[%s] === "undefined");'
            % repr(global_name)
        )

    def click(self, selector, btn=0):
        """Click the targeted element.
        :param selector: A CSS3 selector to targeted element.
        :param btn: The number of mouse button.
            0 - left button,
            1 - middle button,
            2 - right button
        """
        self._checkSelector(selector)
        s = """
            (function () {
                var element = document.querySelector(%s);
                var evt = document.createEvent("MouseEvents");
                evt.initMouseEvent("click", true, true, window, 1, 1, 1, 1, 1,
                    false, false, false, false, %s, element);
                return element.dispatchEvent(evt);
            })();
        """ % (repr(selector), str(btn))
        return self.evaluate(s)

    def wait_for(self, condition):
        """Waits until condition is True.
        :param condition: A callable that returns the condition.
        :param timeout: An optional timeout.
        """
        started_at = time.time()
        while not condition():
            if time.time() > (started_at + self.timeout):
                raise TimeoutError("Timeout until waiting condition")
            self.sleep(0.01)

    def wait_for_selector(self, selector: str):
        """Waits until selector match an element on the frame.
        :param selector: The selector to wait for.
        """
        self.wait_for(
            lambda: self.exists(selector),
            'Can\'t find element matching "%s"' % selector
        )
        return True, self._release_last_resources()

    def _checkSelector(self, selector: str):
        if not self.exists(selector):
            raise SelectorException("No such selector:" + selector)

    def getText(self, selector: str):
        self._checkSelector(selector)
        return self.evaluate("""document.querySelector("%s").innerText""" % (selector))

    def getHtml(self, selector: str):
        self._checkSelector(selector)
        return self.evaluate("""document.querySelector("%s").innerHTML""" % (selector))

    def getOuterHtml(self, selector: str):
        self._checkSelector(selector)
        return self.evaluate("""document.querySelector("%s").outerHTML""" % (selector))

    def setValue(self, selector: str, value: str):
        self._checkSelector(selector)
        return self.evaluate("""document.querySelector("%s").value="%s";""" % (selector, value))

    def getRegion(self, selector: str)->Region:
        self._checkSelector(selector)
        return Region(self.evaluate("""
        (function(){
            var ___elementSize = document.querySelector("%s").getBoundingClientRect();
            ___elementSize.left + ":" + ___elementSize.top + ":" + ___elementSize.width + ":" + ___elementSize.height
        })();
        """ % (selector)))

    def selectorsCount(self, selector):
        return int(self.evaluate("""document.querySelectorAll("%s").length""" % (selector)))

    def waitForPageUnloaded(self):
        gVar = _randStr()
        self.evaluate("window['%s']=1;" % (gVar))
        def unloadedCondition():
            return not self.evaluate("window['%s']" % (gVar))
        self.wait_for(unloadedCondition)


    def fillForm(self, **values):
        """Fills the form with values"""
        for selector in values:
            self.setValue(selector, values[selector])

    def markNumberedSelector(self, selector):
        s = """
            (function(){
                var els = document.querySelectorAll("%s");
                for (var k=0; k<els.length; k++){
                    els[k].setAttribute("%s", k);
                }
            })();
        """ % (selector, self._numberSelector)
        self.evaluate(s)

    def clearNumberedSelectors(self):
        s = """
            (function(){
                var attribute = "%s";
                var selector = "["+attribute+"]";
                var els = document.querySelectorAll(selector);
                for (var k=0; k<els.length; k++){
                    els[k].removeAttribute(attribute);
                }
                return selector;
            })()
        """ % (self._numberSelector)
        self.evaluate(s)

    def genNumberedSelector(self, number):
        return "[%s=\\'%s\\']" % (self._numberSelector, number)


class Browser(object):
    @abstractmethod
    def startSession(self)->Session:
        """Starts new browser session"""

