main_py = """\
#! /usr/bin/env python

from simpleweb import run
import urls

run('fcgi')
"""

config_py = """\
from simpleweb import *
from simpleweb.plugins import dblayer, template, auth


#db_plugin = dblayer.SqlObjectDB('mysql://username:password@hostname:port/databasename?parameters?cache=False')
#db_plugin = dblayer.SqlObjectDB('sqlite:///$projectname.db')
#db_plugin = dblayer.SqlObjectDB('pgsql://username:password@hostname:port/databasename?parameters?debug=True')

template_plugin = template.Cheetah()

auth_plugin = auth.SimpleAuth()

port = 8080
host = '0.0.0.0'

#add other variables here. They will be 
#accessible when you 'import config'
#in your controllers

title = '$projectname'
#myvar = 'value'
"""

urls_py = """\
#urlmap file for $projectname
from simpleweb import urladd

#All the action in simple web happens in application modules
#these map a url to a module file. examples are given below:

urladd('/', 'controllers.index')
#urladd('/blog[/[{id:number}[/]]]', 'blogapplication.main')
"""

models_py= """\
import config
from sqlobject import *
"""

master_html = """\
#def title
$projectname
#end def

#def page
$projectname
#end def

#def body
$projectname
#end def

<html>
<head>
    <title>$$title</title>
    <link type="text/css" media="screen" rel="stylesheet" href="/static/css/main.css"/>
	<style>
		* {
			margin: 0;
			padding: 0;
		}

		body {
			font: verdana, tahoma, sans-serif;
			font-size: 1em;
			margin: 0 auto;
			width: 800px;
		}

		#banner {
			width: 100%;
			height: 50px;
			text-align: right;
			border-color: #ccc;
			border-width: 0.1em;
			border-bottom-style: solid;
		}

		#banner h1 {
			color: #666;
			padding: 0.2em 0.5em 0 0.5em;
		}

		#container {
			margin: 5 auto;
			padding: 0 0.5em 0 0.5em;
		}

		#footer {
			margin: 3 auto;
			border-width: 0.1em;
			border-color: #ccc;
			border-top-style: solid;
		}

		#footer p {
			font-size: 0.9em;
			color: #ccc;
		}

		span {
			padding: 10px;
		}

		ol, ul {
			margin-left: 20px;
		}
			

	</style>
</head>

<body>
	<div id="banner"><h1>$$page</h1></div>
	<div id="container">
			$$body
	</div>
	<div id="footer"> 
		<p>Powered by 'simpleweb'</p>
		<p>Copyright &copy; 2006 Essien Ita Essien</p>
	</div>
</body>

</html>
"""

index_html = """\
#include "master.html"

#def title
	Welcome	
#end def

#def page
$projectname - Default Home
#end def

#def body
	<span>
		<p>
			Hey there! You have just created a new 'simpleweb' project - $projectname. This is the default look and feel.
		</p>
	</span>

	<h2>Get Started Already!</h2>
	<span>
		<p>The following checklist should help you get up and running: </p>
		<p></p>
		<ol>
			<li>Update config.py, choose your Database plugin and Templating plugin</li>
			<li>Define your database models in models.py</li>
			<li>Create your database tables with 'simpleweb-admin createtables'</li>
			<li>Create your controllers in the controllers package</li>
			<li>Map your controllers to urls in urls.py</li>
			<li>Add unittests into the tests/ folders in the toplevel and controllers package</li>
			<li>Modify the master template in templates/master.html</li>
			<li>Add new templates in templates/</li>
		</ol>
	</span>

	<h2>Testing</h2>
	<span>
		<p>
			Running 'nosetests' in the toplevel project folder should do the trick
		</p>
	</span>
			
#end def
"""

index_py = """\
import config
import models

def GET(request):
	return config.template_plugin.render('index.html')
"""
