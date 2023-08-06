"""
Various exceptions used in rdf.

"""

class Error(Exception):
    """Base class for rdf exceptions."""

    def __init__(self, msg=None):
        Exception.__init__(self, msg)
        self.msg = msg


class ParserError(Error):
    """RDF Parser error."""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class UniquenessError(Error):
    """A uniqueness assumption was made in the context, and that is not true"""

    def __init__(self, values):
        Error.__init__(self, "Uniqueness assumption is not fulfilled. \
Multiple values are: %s" % values)


