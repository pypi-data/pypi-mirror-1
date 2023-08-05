import os.path
import simpleweb.settings
from Cheetah.Template import Template

class Cheetah(object):

	def __init__(self, dir="templates"):
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
