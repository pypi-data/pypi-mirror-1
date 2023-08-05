import chattyparallel
from distutils.core import setup

setup(
    name         = 'chattyparallel',
    description  = "Offload tasks to child processes, using a fork based processing model. A variation on Paul Boddie's Parallel.",
    version      = chattyparallel.__version__,
    author       = "Ludovico Magnocavallo",
    author_email = "ludo@qix.it",
    url          = "http://www.python.org/pypi/chattyparallel",
    license      = "MIT",
    classifiers  = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing'],
    py_modules   = ['chattyparallel'],
    )
