# A package

import mimetypes
if ".rst" not in mimetypes.types_map:
    mimetypes.add_type("text/x-rst", ".rst")
