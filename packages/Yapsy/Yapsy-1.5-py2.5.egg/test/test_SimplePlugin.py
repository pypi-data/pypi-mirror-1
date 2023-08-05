import test_settings
import unittest
import os 

from yapsy.PluginManager import PluginManager


class SimpleTestsCase(unittest.TestCase):
	"""
	Test the correct loading of a simple plugin as well as basic
	commands.
	"""
	
	def setUp(self):
		"""
		init
		"""
		# create the plugin manager
		self.simplePluginManager = PluginManager(directories_list=[
				os.path.join(
					os.path.dirname(os.path.abspath(__file__)),"plugins")])
		# load the plugins that may be found
		self.simplePluginManager.collectPlugins()
		# Will be used later
		self.plugin_info = None

	def plugin_loading_check(self):
		"""
		Test if the correct plugin has been loaded.
		"""
		if self.plugin_info is None:
			# check nb of categories
			self.assertEqual(len(self.simplePluginManager.getCategories()),1)
			sole_category = self.simplePluginManager.getCategories()[0]
			# check the number of plugins
			self.assertEqual(len(self.simplePluginManager.getPluginsOfCategory(sole_category)),1)
			self.plugin_info = self.simplePluginManager.getPluginsOfCategory(sole_category)[0]
			# test that the name of the plugin has been correctly defined
			self.assertEqual(self.plugin_info.name,"Simple Plugin")
			self.assertEqual(sole_category,self.plugin_info.category)
		else:
			self.assert_(True)

	def testLoaded(self):
		"""
		Test if the correct plugin has been loaded.
		"""
		self.plugin_loading_check()
		

	def testActivationAndDeactivation(self):
		"""
		Test if the activation procedure works.
		"""
		self.plugin_loading_check()
		self.assert_(not self.plugin_info.plugin_object.is_activated)
		self.simplePluginManager.activatePluginByName(self.plugin_info.category,
													  self.plugin_info.name)
		self.assert_(self.plugin_info.plugin_object.is_activated)
		self.simplePluginManager.deactivatePluginByName(self.plugin_info.category,
														 self.plugin_info.name)
		self.assert_(not self.plugin_info.plugin_object.is_activated)




suite = unittest.TestSuite([
		unittest.TestLoader().loadTestsFromTestCase(SimpleTestsCase),
		])
