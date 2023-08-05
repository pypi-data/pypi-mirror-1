import utils

__all__ = ['Bogus']

class Bogus:
	def foo():
		pass
	pass

def test_get_functions():
	funcs = utils.get_functions('test_utils')
	assert test_get_functions in funcs
	assert Bogus not in funcs

def test_get_methods_dict():
	methods_dict = utils.get_methods_dict('test_utils', ['test_get_functions', 'test_get_methods_dict'])
	assert test_get_methods_dict is methods_dict['test_get_methods_dict']
	assert test_get_functions is methods_dict['test_get_functions']

def test_from_import():
	from plugins import dblayer
	from test_utils import Bogus

	dbl = utils.from_import('plugins.dblayer')
	assert dbl is dblayer

	bg = utils.from_import('test_utils.Bogus')
	print bg.__name__
	print Bogus.__name__
	assert bg is Bogus

