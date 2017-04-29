from pyBrowse.Browser import Session


def nthSelector(selector, num):
    return "%s:nth-of-type(%s)" % (selector, num)
