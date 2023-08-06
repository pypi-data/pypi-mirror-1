# sanitize.py
#
# derived from snippet http://www.djangosnippets.org/snippets/205/
#
# Copyright (C) 2008 Marco Pantaleoni. All rights reserved
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from BeautifulSoup import BeautifulSoup, Comment
import re

def sanitize_html(value, valid_tags = None, valid_attrs = None):
    if valid_tags != '':
        valid_tags = valid_tags or 'p i strong b u a h1 h2 h3 pre br img'
    if type(valid_tags) == type(''):
        valid_tags = valid_tags.split()
    if valid_attrs != '':
        valid_attrs = valid_attrs or 'href src'
    if type(valid_attrs) == type(''):
        valid_attrs = valid_attrs.split()

    soup = BeautifulSoup(value)
    for comment in soup.findAll(
        text=lambda text: isinstance(text, Comment)):
        comment.extract()
    for tag in soup.findAll(True):
        if tag.name not in valid_tags:
            tag.hidden = True
        tag.attrs = [(attr, val) for attr, val in tag.attrs
                     if attr in valid_attrs]
    result = soup.renderContents().decode('utf8')
    result = result.replace('javascript:', '')
    javascript_sanitize_re = re.compile('j[\s]*(&#x.{1,7})?a[\s]*(&#x.{1,7})?v[\s]*(&#x.{1,7})?a[\s]*(&#x.{1,7})?s[\s]*(&#x.{1,7})?c[\s]*(&#x.{1,7})?r[\s]*(&#x.{1,7})?i[\s]*(&#x.{1,7})?p[\s]*(&#x.{1,7})?t', re.IGNORECASE)
    result = javascript_sanitize_re.sub('', result)

    return result
