# Copyright 2009 Chad Daelhousen.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#

import xml.dom.minidom as minidom

class BackgroundData (object):
    _elements = ('filename', 'options', 'shade_type', 'pcolor', 'scolor')
    deleted = False

    def __init__ (self, wp_xml=None):
        self.settings = dict()
        if wp_xml is not None:
            self.parse_node(wp_xml)

    def _fetch_text_list (self, nodelist):
        texts = []

        for i in range(0, nodelist.length):
            text = self._fetch_text(nodelist.item(i))
            if text:
                texts.append(text)

        return ''.join(texts)

    def _fetch_text (self, node):
        if node.nodeType == node.TEXT_NODE:
            return node.data
        else:
            return ''

    def parse_node (self, wp_xml):
        # deleted attribute -> boolean
        deleted = wp_xml.attributes.getNamedItem("deleted").nodeValue
        if deleted == 'true':
            self.deleted = True
        else:
            self.deleted = False

        # name, filename, options, shade_type, pcolor, scolor
        for tagname in self._elements:
            tags = wp_xml.getElementsByTagName(tagname)
            tag = tags[0]

            attr = tag.nodeName
            value = self._fetch_text_list(tag.childNodes)

            self.settings[attr] = value


class BackgroundList (object):
    def __init__ (self, src):
        self.load(src)

    def load (self, file):
        doc = minidom.parse(file)

        tags = doc.documentElement.getElementsByTagName("wallpaper")
        self.items = [BackgroundData(tag) for tag in tags]
        self._all_items = self.items[:]

        doc.unlink()

    def filter (self, predicate_list=None):
        if predicate_list is None or len(predicate_list) == 0:
            return

        for predicate in predicate_list:
            self.items = [item for item in self.items if predicate(item)]

    def reset (self):
        self.items = self._all_items[:]

