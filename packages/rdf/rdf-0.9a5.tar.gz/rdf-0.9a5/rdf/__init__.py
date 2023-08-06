"""\
A pure Python package providing the core RDF constructs.

The packages is intended to provide the core RDF types and interfaces
that other packages can build on. The package defines a plugin
interface for parsers, stores, and serializers that other packages can
use to implement parsers, stores, and serializers that will plug into
the rdf package.

The `rdf` package does not itself contain any plugin
implementation. So, you will want to install a library that builds
upon `rdf` and defines some plugin implementations. One such library
is `rdflib` version 3.x.

The primary interface `rdf` exposes to work with RDF is
`rdf.graph.Graph`.

A tiny example:


    >>> from rdf.graph import Graph

    >>> g = Graph()
    >>> result = g.parse("http://eikeon.com/foaf.rdf")

    >>> print "graph has %s statements." % len(g)
    graph has 34 statements.
    >>>
    >>> for s, p, o in g:
    ...     if (s, p, o) not in g:
    ...         raise Exception("It better be!")

    >>> s = g.serialize(format='n3')

"""

__version__ = "0.9a5"
__docformat__ = "restructuredtext en"

