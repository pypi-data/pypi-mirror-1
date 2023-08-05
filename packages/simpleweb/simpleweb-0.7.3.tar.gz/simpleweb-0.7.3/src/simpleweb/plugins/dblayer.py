import sys
import simpleweb.utils

def get_models():
	sys.path.insert(0, '.')
	try:
		return __import__('models')
	except ImportError, e:
		simpleweb.utils.msg_err("Could not successfully import 'models.py': %s" % (e))
		sys.exit(1)

def get_tables_from_model(model, tabletype):
	for(name, table) in vars(model).iteritems():
		if isinstance(table, tabletype):
			yield table

def do_table_function(table, funcname, ex, errmsg, **kw):
	try:
		func = getattr(table, funcname)
		func(**kw)
	except ex, e:
		simpleweb.utils.msg_warn(errmsg + ": %s." % (e))

class SqlAlchemyDB(object):
	def __init__(self, dburi):
		try:
			import sqlalchemy
		except ImportError:
			simpleweb.utils.optional_dependency_err('SqlAlchemyDB', 'sqlalchemy')
		else:
			self.metadata = sqlalchemy.BoundMetaData(dburi)

	def get_tables(self):
		import sqlalchemy
		models = get_models()
		for t in get_tables_from_model(models, sqlalchemy.Table): 
			yield t

	def createtables(self):
		import sqlalchemy
		models = get_models()
		for t in self.get_tables(): 
			do_table_function(t, 'create', sqlalchemy.exceptions.SQLError, "Table %s already exists" % (t))

	def droptables(self):
		import sqlalchemy

		models = get_models()
		tables = get_tables_from_model(models, sqlalchemy.Table)
		for t in tables:
			do_table_function(t, 'drop', sqlalchemy.exceptions.SQLError, "Error dropping table %s" % (t))


class SqlObjectDB(object):
	def __init__(self, dburi):
		try:
			import sqlobject
		except ImportError:
			simpleweb.utils.optional_dependency_err('SqlObjectDB', 'sqlobject')
		else:
			self.connection = sqlobject.connectionForURI(dburi)
			sqlobject.sqlhub.processConnection = self.connection

	def get_tables(self):
		import sqlobject
		models = get_models()
		for t in get_tables_from_model(models, sqlobject.declarative.DeclarativeMeta):
			if t is sqlobject.main.SQLObject or t is sqlobject.main.sqlmeta:
				continue
			else:
				yield t

	def createtables(self):
		import sqlobject
		models = get_models()
		for t in self.get_tables():
			do_table_function(t, 'createTable', Exception, "Error creating table: %s" % (t), ifNotExists=True)

	def droptables(self):
		import sqlobject

		models = get_models()
		tables = get_tables_from_model(models, sqlobject.declarative.DeclarativeMeta)
		for t in tables: 
			if t is sqlobject.main.SQLObject or t is sqlobject.main.sqlmeta: 
				continue			
			do_table_function(t, 'dropTable', Exception, "Error dropping table %s" % (t))


