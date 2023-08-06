#!/usr/bin/python

# Yould - A name generator generator
# This program was initially written by © Yannick Gingras - 2007

# Is was adapted by © Arne Babenhauserheide in 2007. 

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
# MA 02110-1301 USA

from urllib import urlopen
from re import compile

# Different compilations from gutenberg.org

# Esperanto

books_esperanto = [17665, 18178, 20802, 17482, 11511, 8177, 20931, 21194, 19183, 20178, 20162, 19858, 19803, 19030, 19182, 19293, 21195, 21951, 17425, 18326, 20943, 17945, 18836, 11307, 20006, 8224]

# marion zimmer bradley, flatland. 
books_english_science_fiction = [20796, 19726, 97]

books_english_romantic_poetry = [18500, 4800, 8209, 20158, 9622]

books_english_erotic_classic = [5225, 3726]

books_english_erotic_modern = [20028, 16885, 7889, 6852, 4300]

# King James Bible
books_english_bible = [8010, 8011, 8012, 8013, 8014, 8015, 8016, 8017, 8018, 8019,
         8001, 8020, 8021, 8022, 8023, 8024, 8025, 8026, 8027, 8028,
         8029, 8002, 8030, 8031, 8032, 8033, 8034, 8035, 8036, 8037,
         8038, 8039, 8003, 8040, 8041, 8042, 8043, 8044, 8045, 8046,
         8047, 8048, 8049, 8004, 8050, 8051, 8052, 8053, 8054, 8055,
         8056, 8057, 8058, 8059, 8005, 8060, 8061, 8062, 8063, 8064,
         8065, 8066, 8006, 8007, 8008, 8009]

BOOKS = books_esperanto
PATH = "Esperanto" #: Path inside the download-directory. 

BASE_URL = "http://www.gutenberg.org/"
MAIN_URL = BASE_URL + "etext/%d"
DL_PAT = compile(r'<td class="pgdbfilesdownload"><a href="(/(?:dirs|files)/.*?.txt)"')
MAX = 2**22

for book in BOOKS:
    try:
        data = urlopen(MAIN_URL % book).read(MAX)
        print "Book:", book
        dl = DL_PAT.findall(data)[0]
        print 'File to download:', dl
        path = "training_materials/gutenberg_downloads/" + PATH + "/%04d.txt" % book
        print "Local Path:", path
        stream = urlopen(BASE_URL + dl)
        open(path, "w").write(stream.read(MAX))
    except:
        print "Error"
    
