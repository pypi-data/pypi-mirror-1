# Copyright (C) 2008-2009 John Millikin <jmillikin@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re

CSS_DELIMS = '\({};:,'
CSS_COMMENT_RE = re.compile ('\/\*.*?\*\/', re.DOTALL | re.MULTILINE)
CSS_WHITESPACE_RE = re.compile ('\s+', re.MULTILINE)
CSS_ADJ_WHITESPACE_RE = re.compile ('\s?([%s])\s?' % CSS_DELIMS)
def compress_css (text):
	"""Minify CSS by removing comments and whitespace."""
	text = CSS_COMMENT_RE.sub ('', text)
	text = CSS_WHITESPACE_RE.sub (' ', text)
	text = CSS_ADJ_WHITESPACE_RE.sub ('\\1', text)
	
	return text
	
