import os.path
from Cheetah.Template import Template

class Cheetah(object):

	def __init__(self, dir="templates"):
		self.dir = dir
		
	def render(self, template, **kw):
		template_dir = os.path.join(os.getcwd(), self.dir)	
		pwd = os.getcwd()
		os.chdir(template_dir)
		try:
			t = Template(file=template, searchList=[kw])
			t = str(t)
		finally:
			os.chdir(pwd)

		return t
