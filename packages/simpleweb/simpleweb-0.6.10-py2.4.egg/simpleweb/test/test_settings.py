import settings

a = 5
b = 4

class TestConfig(object):
	def test_load(self):
		s = settings.Config('test_settings')
		assert s.a == a
		assert s.b == b




