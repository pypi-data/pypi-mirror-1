
from xml.dom import minidom as dom

import logging
log = logging.getLogger(__file__)

# the following try/except import tree was taken from the lxml
#  tutorial.
"""
try:
	from lxml import etree
	log.debug("running with lxml.etree")
except ImportError:
	try:
		# Python 2.5
		import xml.etree.cElementTree as etree
		log.debug("running with cElementTree on Python 2.5+")
	except ImportError:
		try:
			# Python 2.5
			import xml.etree.ElementTree as etree
			log.debug("running with ElementTree on Python 2.5+")
		except ImportError:
			try:
				# normal cElementTree install
				import cElementTree as etree
				log.debug("running with cElementTree")
			except ImportError:
				try:
					# normal ElementTree install
					import elementtree.ElementTree as etree
					log.debug("running with ElementTree")
				except ImportError:
					log.error("Failed to import ElementTree from any known place")
					raise
"""
from lxml import etree

# I'm considering creating an emulator for the etree interface
# so that earlier versions of Python won't have any additional
# dependencies.
class MinidomEtreeEmulator(object):
	pass