#VERSION: 2.22
#AUTHORS: Yukarin (yukariin@yandex.ru)

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# * Neither the name of the author nor the names of its contributors may be
# used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
from sgmllib3 import SGMLParser


class nyaatorrents(object):
    url = 'http://www.nyaa.se'
    name = 'Nyaatorrents'
    supported_categories = {'all': '0_0', 'anime': '1_0', 'books': '2_0',
                            'music': '3_0', 'pictures': '4_0',
                            'software': '6_0', 'games': '6_24'}

    def download_torrent(self, info):
        print(download_file(info))

    class SimpleSGMLParser(SGMLParser):
        def __init__(self, results, url):
            SGMLParser.__init__(self)
            self.td_counter = None
            self.current_item = None
            self.results = results
            self.url = url

        def start_a(self, attr):
            params = dict(attr)
            if 'href' in params:
                if 'page=download' in params['href']:
                    self.current_item['link'] = params['href'].strip()
                elif 'page=view' in params['href']:
                    self.current_item = {}
                    self.td_counter = 0
                    self.current_item['desc_link'] = params['href'].strip()

        def handle_data(self, data):
            if self.td_counter == 0:
                if 'name' not in self.current_item:
                    self.current_item['name'] = ''
                self.current_item['name'] += data
            elif self.td_counter == 2:
                if 'size' not in self.current_item:
                    self.current_item['size'] = ''
                self.current_item['size'] += data.strip()
            elif self.td_counter == 3:
                if 'seeds' not in self.current_item:
                    self.current_item['seeds'] = ''
                self.current_item['seeds'] += data.strip()
            elif self.td_counter == 4:
                if 'leech' not in self.current_item:
                    self.current_item['leech'] = ''
                self.current_item['leech'] += data.strip()

        def start_td(self, attr):
            if isinstance(self.td_counter, int):
                self.td_counter += 1
                if self.td_counter > 4:
                    self.td_counter = None
                    if self.current_item:
                        self.current_item['engine_url'] = self.url
                        if not self.current_item['seeds'].isdigit():
                            self.current_item['seeds'] = 0
                        if not self.current_item['leech'].isdigit():
                            self.current_item['leech'] = 0
                        prettyPrinter(self.current_item)
                        self.results.append('a')

    def search(self, what, cat='all'):
        i = 1
        while True and i < 11:
            results = []
            parser = self.SimpleSGMLParser(results, self.url)
            dat = retrieve_url(self.url + '/?page=search&term=%s&offset=%d&cats=%s' % (what, i, self.supported_categories[cat]))
            parser.feed(dat)
            parser.close()
            if len(results) <= 0:
                break
            i += 1
