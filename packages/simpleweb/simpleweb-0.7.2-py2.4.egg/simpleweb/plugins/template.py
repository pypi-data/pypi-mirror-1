import sys
import os.path
import simpleweb.settings
import simpleweb.utils

plugins = {}

try:
	from Cheetah.Template import Template
	plugins['Cheetah'] = Template
except ImportError:
	pass
	

class Cheetah(object):

	def __init__(self, dir="templates"):
		if not plugins.has_key('Cheetah'):
			simpleweb.utils.optional_dependency_err('Cheetah Template Plugin', 'Cheetah')

		self.dir = dir
		
	def render(self, template, **kw):
		config = simpleweb.settings.Config("config")
		template_dir = os.path.join(config.working_directory, self.dir)	
		os.chdir(template_dir)
		try:
			t = Template(file=template, searchList=[kw])
			t = str(t)
		finally:
			os.chdir(config.working_directory)

		return t
