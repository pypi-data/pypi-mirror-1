import doctest
from doctest import DocFileSuite
flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE)
def test_suite():
    return DocFileSuite(
        "browser.txt",
        optionflags = flags
    )
