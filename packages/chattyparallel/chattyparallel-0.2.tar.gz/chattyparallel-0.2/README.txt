Introduction
------------

Chattyparallel is a variation on Paul Boddie's parallel that uses a
fork-based process creation model, and channel-based communications to
offload tasks to child processes. It should be an easy replacement for
threads in scripts that perform lots of simple network operations, like
feed crawlers or automated HTTP clients.

Quick Start
-----------

A very simple example is included in the module as a doctest unit test. To run it,
simply launch the module:

python chattyparallel.py

Changes
-------

* 0.2 (April 4, 2007)
  
  - fix handling of POLLHUP events

Contact, Copyright and Licence Information
------------------------------------------

You can contact me at the following address:

ludo@qix.it

Copyright (c) 2007 Ludovico Magnocavallo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
