from iqpp.rating.config import ENCODING

def stringToUnicode(string):
    """
    """
    if string is None:
        return None

    if isinstance(string, unicode):
        return string

    return unicode(string, ENCODING)