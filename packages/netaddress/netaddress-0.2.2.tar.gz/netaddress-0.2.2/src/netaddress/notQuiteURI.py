from rfc3986 import scheme, reg_name, port, host, path_abempty
from pyparsing import Combine, Literal, Optional

primitiveHost = reg_name.setResultsName("host")
path = path_abempty.setResultsName("path")

primitiveURI = scheme + Literal("://") + primitiveHost + path

# URI grammar as used in angel-app
angelURI = Literal("http://") + host + Optional(Literal(":") + port)
