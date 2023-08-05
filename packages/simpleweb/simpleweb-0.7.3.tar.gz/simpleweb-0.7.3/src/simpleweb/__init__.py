"""
A simple, highly pluggable RESTafarian web framework, built by reusing known components

In simpleweb, the underlying priciple small applications that do one thing and do it well.
Each url is mapped to a single module which should contain the application entrypoint. This
means that while the application can be spread over various modules, it should have the main
methods (GET, POST, PUT, DELETE), in one file that the url is mapped to.

For instance:

urlmap('/user[/[{id}[/]]]', 'crm.users')
urlmap('/client[/[{id}[/]]]', 'crm.client')
urlmap('/blog[/[{id}[/]]]', 'blogengine.blog')
urlmap('/blog/{id}/comment[/[{id}[/]]]', 'blogengine.comment')

Each of the url handlers (aka controllers) do just one thing only, 
they publish the methods for GET, POST, PUT and DELETE. They are obviously
part of packages in this instance, but they *should* be refactored to make wholesome
sense in the api they publish.
"""
import settings
import _urls


__all__ = [
		'urladd', 
		'run'
		]

urladd = _urls.urladd

def run(method='development'):
	import plugins.runmethods
	config = settings.Config("config")
	runmethods = getattr(plugins.runmethods, method)
	runmethods(_urls, config)
