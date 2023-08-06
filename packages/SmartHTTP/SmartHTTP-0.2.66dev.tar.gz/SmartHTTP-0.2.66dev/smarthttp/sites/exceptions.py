# -*- coding: utf-8 -*-
"""
Parsing exceptions
"""
class ParseException(Exception):
    pass
class XPathException(ParseException):
    pass
class HTTPException(ParseException):
    pass
class HTMLException(ParseException):
    pass
