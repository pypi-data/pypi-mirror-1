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

from os.path import join
import logging
from django.conf import settings
from ..util import load_module_attr

__all__ = ['compress']

log = logging.getLogger (__name__)

FILTER_CACHE = {}
def get_filters (mimetype):
	if mimetype in FILTER_CACHE:
		return FILTER_CACHE[mimetype]
	try:
		filter_names = settings.RESOURCE_COMPRESSION_FILTERS[mimetype]
	except (AttributeError, KeyError):
		filters = []
	else:
		filters = map (load_module_attr, filter_names)
		
	FILTER_CACHE[mimetype] = filters
	return filters
	
def safe_read (path):
	full_path = join (settings.MEDIA_ROOT, path)
	try:
		return open (full_path, 'rb').read ()
	except IOError, exc:
		log.error ("Couldn't compress file %r: %s", full_path, exc,
		           exc_info = True)
		return ""
		
def compress (mimetype, files):
	text = ''.join (safe_read (f) for f in files)
	for func in get_filters (mimetype):
		text = func (text)
	return text
	
