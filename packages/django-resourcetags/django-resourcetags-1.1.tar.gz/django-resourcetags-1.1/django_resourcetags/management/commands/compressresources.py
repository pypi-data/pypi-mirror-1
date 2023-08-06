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

from django.core.management.base import NoArgsCommand
from django.conf import settings

class Command (NoArgsCommand):
	help = "Re-compresses all available resource groups."
	args = ""
	
	def _get_resources (self):
		from Hermes.media import CompressedResourceFactory
		
		factory = CompressedResourceFactory ()
		groups = getattr (settings, 'RESOURCE_GROUPS', {})
		extra = getattr (settings, 'COMPRESS_EXTRA', ())
		for name in groups:
			for resource in factory.get_resource_group (name):
				yield resource
		for name in extra:
			yield factory.get_resource (name)
			
	def handle_noargs (self, **options):
		for resource in self._get_resources ():
			resource.regenerate ()
			
