import os
from simpleweb.admin.plugins import create_movable
import test_create_movable

def test_is_in_current_app():
	class dummy:
		__doc__ = 'A dummy object to pass the is_current_app criteria'
		__file__ = './foo/bar.py'
		pass

	amodule = dummy()
	print amodule.__file__
	assert create_movable.is_in_current_app(amodule) is True


def test_is_package():
	import simpleweb
	assert create_movable.is_package('simpleweb', simpleweb) is True

	import os.path
	assert create_movable.is_package('os.path', os.path) is False

def test_build_pkg_path():
	assert create_movable.build_pkg_path('a.b.c') == 'a/b/c'

def test_is_nested_module():
	import simpleweb.webserver
	assert create_movable.is_nested_module('simpleweb.webserver', simpleweb.webserver) is True

	import email
	assert create_movable.is_nested_module('email', email) is False

def test_build_nested_module_path():
	assert create_movable.build_nested_module_path('a.b.c') == 'a/b'

def test_conv_obj2src():
	filename = 'afilename.pyc'
	filename2 = 'afilename.pyo'
	filename3 = 'afilename.py'

	assert create_movable.conv_obj2src(filename) == 'afilename.py'
	assert create_movable.conv_obj2src(filename2) == 'afilename.py'
	assert create_movable.conv_obj2src(filename3) == 'afilename.py'

def test_get_module_file():
	import test_create_movable
	test_create_movable_filename = create_movable.get_module_file(test_create_movable)
	test_create_movable_file = open(test_create_movable_filename, 'r')
	test_create_movable_contents = test_create_movable_file.read()
	test_create_movable_file.close()

	this_file_name = create_movable.conv_obj2src(__file__)
	this_file = open(this_file_name, 'r')
	this_contents = this_file.read()
	this_file.close()

	print '----------------------------'
	print test_create_movable_contents
	print '----------------------------'
	print this_contents
	assert test_create_movable_contents == this_contents

def test_create_pkg_dir():
	root_dir = 'root_dir'
	path1 = create_movable.create_pkg_dir('a.b.c', root_dir=root_dir, dummy_run=True)
	assert path1 == os.path.join(root_dir, 'a', 'b', 'c')

	path2 = create_movable.create_pkg_dir('a.b.c', root_dir=root_dir, is_pkg=False, dummy_run=True)
	assert path2 == os.path.join(root_dir, 'a', 'b')
