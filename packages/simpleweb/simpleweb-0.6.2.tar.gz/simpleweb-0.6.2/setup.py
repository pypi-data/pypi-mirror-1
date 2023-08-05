from setuptools import setup, find_packages


setup (
		name = "simpleweb",
		version = "0.6.2",
		packages = find_packages('src'),
		package_dir = {'':'src'},
		include_package_data = True,
		package_data = {
			'': ['TODO', 'BUGS', 'ChangeLog', 'test/*.py'],
			'plugins':['test/*.py'],
			'admin.plugins':['test/*.py']
		},

		install_requires = ['selector', 'yaro', 'static', 'flup', 'sqlobject', 'sqlalchemy', 'Cheetah', 'wsgiref'],


		author = "Essien Ita Essien",
		author_email = "me@essienitaessien.com",
		license = "BSD",
		description = "A simple python wsgi compliant web framework, inspired by Django, Turbo Gears and Web.py",
		keywords = "web framework simple cheetah sqlobject",
		url = "http://simpleweb.essienitaessien.com",

		long_description = """
		simpleweb is a result of working closely with web.py, TurboGears, Django,
		and a very hefty dose of opinionation(tm) :)

		Like TurboGears, it builds on existing python and wsgi components, 
		to keep things simple, and just connects these components in a very 
		easy transparent way.

		Like web.py its dispatching mechanism is matched strictly to HTTP methods.

		Like Django, its built for building deadline(s)-oriented(tm) applications. 
		As such, working with simpleweb will have a certain sense of deja-vu if you've
		worked much Django, there are differences ofcourse, but the general feel is
		the same.
		""",

		entry_points = {
			'console_scripts' : [
				'simpleweb-admin = simpleweb.admin.console:main'
				]
			}

		)
