PyWebRun - Python Web Runner (version 0.0.2 - 2008.02.02)
"Running Python scripts over HTTP"


Public domain (P) 2008 Davide Rognoni

DAVIDE ROGNONI DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS, IN NO EVENT SHALL DAVIDE ROGNONI BE LIABLE FOR
ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
THIS SOFTWARE.

E-mail: davide.rognoni@gmail.com


NEWS
----
Tested on Vista.
Tested with PyternetBrowser version 0.0.4


FILES LIST
----------
src/cache/cache.txt
src/cache.py          files stored system with SQLite
src/gui.gif
src/gui.py            user interface made with wxPython
src/server.bat        SimpleHTTPServer for test
src/test.py
history.txt
README.txt


DEPENDENCES
-----------
Python 2.5.1 (contains SQLite3)
wxPython 2.8.7.1


TUTORIAL
--------
Unzip the archive PyWebRun-x.x.x.tar.gz and open a console in the unzipped SRC folder:
PyWebRun/src

Type in your console (for windows):

server.bat

(for linux to see inside server.bat)
It run a local HTTP server:

Serving HTTP on 0.0.0.0 port 8000 ...

Test with your browser the URL http://localhost:8000
Open a new console in SRC folder and type

python gui.py

It run the user interface "PyWebRun - Python Web Runner" (GUI).
Type in GUI:

run http://localhost:8000/test.py

The command open the test frame "HELLO! Test"
end show in output:

cmd> run http://localhost:8000/test.py
downloading http://localhost:8000/test.py
downloaded as a0057d79e8adb11dc9856444553540000.py
HELLO!
downloading http://localhost:8000/gui.gif
downloaded as a02c3595e8adb11dcb039444553540000.gif

Close the test frame.
Go on GUI, focus on commands field, press KEY DOWN.
This show the last command, press ENTER.

The command re-open the test frame "HELLO! Test" from cache
end show in output:

cmd> run http://localhost:8000/test.py
get http://localhost:8000/test.py
from cache a0057d79e8adb11dc9856444553540000.py
HELLO!
get http://localhost:8000/gui.gif
from cache a02c3595e8adb11dcb039444553540000.gif

Go in CACHE folder PyWebRun/src/cache and read cache.txt
