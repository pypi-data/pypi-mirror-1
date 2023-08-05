PyderWeb (version 0.0.1 - 2007.11.30)
"the robot spider of web"

Public domain (P) 2007 Davide Rognoni

DAVIDE ROGNONI DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS, IN NO EVENT SHALL DAVIDE ROGNONI BE LIABLE FOR
ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
THIS SOFTWARE.

E-mail: davide.rognoni@gmail.com


FILES LIST
----------
src/PyderWeb.py   web spider
src/server.py     ThreadingHTTPServer for test
README.txt


DEPENDENCES
-----------
Python 2.5.1


TUTORIAL
--------
Type in your console:
python server.py

It run a local proxy server:
Serving HTTP on 0.0.0.0 port 8000 ...

Type in another console:
python PyderWeb.py

It will find all links:
[[{'href': 'http://localhost:8000/one'}, 'One'], [{'href': 'http://localhost:800
0/two'}, 'Two\n'], [{'href': 'ftp://'}, 'One']]
