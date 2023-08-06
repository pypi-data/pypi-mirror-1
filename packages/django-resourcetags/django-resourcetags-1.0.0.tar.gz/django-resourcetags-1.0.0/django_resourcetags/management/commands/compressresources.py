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
			
