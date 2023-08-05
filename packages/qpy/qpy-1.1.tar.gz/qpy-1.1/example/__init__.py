# Ensure that all .qpy files in this directory are, when imported, up-to-date.
from qpy.compile import compile_qpy_files
compile_qpy_files(__path__[0])

