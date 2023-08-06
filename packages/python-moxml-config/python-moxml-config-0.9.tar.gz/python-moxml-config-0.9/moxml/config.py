# 
# Copyright (C) 2008 Martin Owens
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# 

'''
XML Based Configuration manager, Very useful xml manager
allows a program to have and manage data sources which
are translated from/to xml/python structures transparently.
'''

from xml.dom import minidom
import binascii
import os, sys, locale
import atexit, time

__version__ = "0.9"

class DefaultManager:
	"""
	DefaultManager is just a slim file save/load class but it allows
	configs to be managed in other ways by using different managers.
	"""
	def load(self, filename):
		if os.path.isfile(filename):
			try:
				fh = open(filename, 'rb')
				if fh:
					return fh.read()
			except:
				return sys.stderr.write("Unable to read file %s: Permission denied\n" % filename)
		sys.stderr.write("Unable to read file %s: File doesn't exist\n" % filename)

	def save(self, filename, data):
		dir = self.directory(filename)
		if os.path.isdir(dir) or dir == '':
			try:
				fh = open(filename, 'wb')
				if fh:
					return fh.write(data)
			except:
				return sys.stderr.write("Unable to write file %s: permission denied\n" % str(filename))
		sys.stderr.write("Unable to write file %s: Directory doesn't exist\n" % str(filename))

	def directory(self, filename):
		return '/'.join(filename.split('/')[:-1])



class Directory:
	'''
	Directory Manager, has a number of classes for managing directories
	which are used by config.py to know where to hold files which are
	related (included from one xml file to another)
	'''
	def __init__(self, directory, autoCreate=False):
		directory = str(directory)
		self.enabled = False

		if directory=='':
			self.enabled = True

		if os.path.exists(directory):
			if os.path.isdir(directory):
				self.enabled = True
		elif autoCreate:
			self.enabled = self.makePath(directory)
			
		if not self.enabled:
			self.directory_not_exist(directory)
		else:
			self.directory = directory

	
	def directory_not_exist(self, directory):
		sys.stderr.write(" ! Directory '" + directory + "' does not exist!\n")


	def load(self, filename):
		if self.enabled:
			path = self.directory + '/' + filename
			if self.fileExists(filename):
				try:
					file = open(path, 'rb')
					return file.read()
				except:
					sys.stderr.write("Unable to read to file %s\n" % filename)
					return ''
		else:
			sys.stderr.write("Failed to load: %s\n" % filename)


	def save(self, filename, contents):
		if self.enabled:

			path = self.directory + '/' + filename
			directory = os.path.dirname(path)

			if not self.makePath( directory ):
				sys.stderr.write(" ! Unable to create directory: %s\n" % directory)
				return False

			try:
				file = open(path, 'wb')
				return file.write(contents)
			except:
				sys.stderr.write(" ! Unable to write to file %s\n" % filename)
				return False
		else:
			sys.stderr.write(" ! Failed to save: %s\n" % filename)

	def makePath(self, directory):
		if not os.path.exists(directory):
			try:
				os.makedirs(directory)
				return True
			except:
				sys.stderr.write(" ! Unable to create directory %s\n" % directory)
				return False
		return True

	def exists(self, thing):
		return os.path.exists(self.directory + '/' + thing)

	def fileExists(self, file):
		return self.exists(file) and os.path.isfile(self.directory + '/' + file)

	def directoryExists(self, directory):
		return self.exists(file) and os.path.isdir(self.directory + '/' + directory)

	def __str__(self):
		return self.directory



class Base:
	"""
	Base class which will include the ability to
	Handle the data being in seperate files.
	"""
	def __init__(self, data, **options):
		self._manager    = options.has_key('manager')  and options['manager']  or None
		self._filename   = options.has_key('filename') and options['filename'] or None
		self._parent     = options.has_key('parent')   and options['parent']   or None
		self._isroot     = not options.has_key('parent') or not options['parent']
		self._loaded     = options.has_key('loaded')   and options['loaded']   or False
		self._version    = options.has_key('version')  and options['version']  or None
		self._changed    = False
		self._subchanged = {}
		self._subfiles   = {}
		self._loadAll    = False

		if isinstance(data, minidom.Element):
			self.set_attributes(data)
			if data.getAttribute('file'):
				self._filename = data.getAttribute('file')
			else:
				self.set_xml(data)
		else:
			self.set(data)

		# Make sure to register us with the parent list of sub files
		if self.filename() and self.parent():
			self.parent().addSubFile(self.filename(), self)

	def saveOnExit(self):
		atexit.register( self.save )

	def parent(self):
		if self._parent != None:
			return self._parent
		return None

	def root(self):
		if self.isRoot():
			return self
		else:
			if self.parent() != None:
				return self.parent().root()
			else:
				sys.stderr.write('This is a fragment, it doesnt have a root\n')
				return self

	def isRoot(self):
		return self._isroot

	def fileRoot(self):
		if self.filename():
			return self
		else:
			if self.parent()!=None:
				return self.parent().fileRoot()
		# Assume current node is root
		return self

	def filename(self):
		return self._filename

	def manager(self):
		if self._manager:
			return self._manager
		elif not self.isRoot():
			return self.root().manager()

	def setManager(self, manager):
		self.fileRoot()._manager = manager

	def save(self):
		if not self._filename:
			return self.fileRoot().save()
		else:
			if self.changed():
				result = self._save_all()
			#else:
				#sys.stderr.write(  "There are no changes to %s, not saving\n" % self._filename )
			if self.subFiles():
				for filename in self.subFiles().keys():
					child = self.subFiles()[filename]
					child.save()

	def _save_all(self):
		if self._filename:
			self._save_me()

	def to_xml(self):
		doc = minidom.Document()
		doc.filename = self._filename
		self.clearSubFiles()
		root = self.get_xml(doc, 'config')
		# Set a new version if we have changed
		root.setAttribute('version', str(self.changed() and self.newVersion() or self.version()))
		doc.appendChild(root)
		return doc.toxml()

	def _save_me(self):
		if self._loaded:
			self._version = self.newVersion()
			self.manager().save(self._filename, self.to_xml())
			self.hasChanged(False)
		else:
			sys.stderr.write( "Not saving " + self._filename + " Not loaded so not required to save\n")

	def saveAs(self, filename):
		self._filename = filename
		self.manager().save(filename, self.to_xml())

	def load(self):
		file = self.manager().load(self._filename)
		if file:
			self.updateWithXML(file)
		else:
			self.set(self.default())
		self._loaded = True

	def loadAll(self):
		ret = self.get()
		for fileobj in self._subfiles.values():
			fileobj.loadAll()
		return ret

	def set(self, value):
		self.value = value
		
	def get(self):
		if self._filename and not self._loaded:
			self.load()
		return self.value

	def set_attributes(self, xmldoc):
		pass

	def version(self):
		if not self._filename:
			return self.fileRoot().version()
		else:
			if self._version:
				return self._version
			return 1

	def newVersion(self):
		return str(int(time.time()))

	def changed(self):
		return self.fileRoot()._changed

	def hasChanged(self, changed=True):
		self.fileRoot()._changed = changed
		if not self.isRoot():
			self.parent().hasSubChanged(changed, self.filename())

	def subchanged(self, filename):
		frsc = self.fileRoot()._subchanged
		return frsc.has_key(filename) and frsc.has_key(filename)

	def hasSubChanged(self, changed, filename):
		self.fileRoot()._subchanged[filename] = changed
		if not self.isRoot():
			self.parent().hasSubChanged(changed, filename)

	def children(self):
		return []

	def subFiles(self):
		return self.fileRoot()._subfiles

	def addSubFile(self, filename, child):
		self.fileRoot()._subfiles[filename] = child

	def removeSubFile(self, filename):
		frsf = self.fileRoot()._subfiles
		if frsf.has_key(filename):
			del(frsf[filename])

	def clearSubFiles(self):
		self.fileRoot()._subfiles = {}

	def updateWithXML(self, xml):
		xmldoc = minidom.parseString(xml)
		for child in xmldoc.childNodes:
			if child.nodeType==1:
				if child.tagName=='config':
					self.set_xml(child)

	# Call Back update, used from standard callback methods
	# to indicate that one of the files has changed and needs
	# updating; mostly via internet or some other reason.
	def cbUpdate(self, xml, options):
		if options['filename'] == self.filename():
			self.updateWithXML(xml)
		else:
			if self._subfiles.has_key(options['filename']):
				self._subfiles[options['filename']].updateWithXML(xml)
			else:
				for subfile in self._subfiles.values():
					subfile.cbUpdate(xml, options)


	def __str__(self):
		return str(self.get())

	def __eq__(self, y):
		return self.value==y

	def __int__(self):
		return int(self.value)

	def __nonzero__(self):
		return True

# Create a child from an xml element
class XMLChild(object):
	def __new__(cls, xmldoc, **options):
		child = None
		if xmldoc.getAttribute('array'):
			child = Array(xmldoc, **options)
		elif xmldoc.getAttribute('type'):
			child = XMLValue(xmldoc, **options)
		else:
			child = Hash(xmldoc, **options)
		return child


# Create a child from an xml value element
class XMLValue(object):
	def __new__(self, data, **options):
		vtype = data.getAttribute('type')
		if vtype=='string':
			return ValueString(data, **options)
		elif vtype=='language':
			return ValueLanguage(data, **options)
		elif vtype=='number':
			return ValueNumber(data, **options)
		elif vtype=='binary':
			return ValueBinary(data, **options)
		else:
			sys.stderr.write("ERROR: unknown type " + vtype + "\n")


# Create a child from a python data class
class NChild(object):
	def __new__(cls, child, **options):
		# Make sure all children are objectified
		if not isinstance(child, Base):
			if isinstance(child, list):
				child = Array(child, **options)
			elif isinstance(child, dict):
				child = Hash(child, **options)
			elif isinstance(child, str):
				child = ValueString(child, **options)
			elif isinstance(child, int):
				child = ValueNumber(child, **options)
			elif isinstance(child, binary):
				child = ValueBinary(child, **options)
			elif child:
				try:
					child = ValueString(str(child), **options)
				except:
					child = ValueString('', **options)
			else:
				child = ValueString('', **options)
		return child

# Load a base file config
class Config(object):
	def __new__(cls, filename, manager=None, default={}):

		config = None
		file   = None

		if not manager:
			manager = DefaultManager()

		if manager and filename:
			if type(manager) == str:
				manager = Directory(manager)
			file = manager.load(filename)

		version = 1
		if file:
			config = newConfig(file, filename, manager, True)
		
		if config == None:
			config = newConfig(default, filename, manager, False)

		return config

# Generate a config based on a new data structure
class newConfig(object):
	def __new__(cls, data, filename, manager=None, existing=False):

		if not manager:
			manager = DefaultManager()

		config = None
		if type(data) is str and data[:5] == '<?xml':

			try:
				xmldoc = minidom.parseString(data)
			except:
				sys.stderr.write("Error when trying to parse xml file %s, corrupt file.\n" % str(filename))
				xmldoc   = False
				existing = False
				data     = {}

			if xmldoc:
				for child in xmldoc.childNodes:
					if child.nodeType==1:
						if child.tagName=='config':
							# Load a parentless bastard class
							config = XMLChild(
								child,
								root     = True,
								filename = filename,
								manager  = manager,
								loaded   = True,
								version  = child.getAttribute('version'),
							)
		else:
			config = NChild(
				data,
				root     = True,
				filename = filename,
				manager  = manager,
				loaded   = True,
			)

		if config != None:
			# Make sure new configs are marked as changed
			config.hasChanged( not existing )
		return config

		
class Hash(Base, dict):
	def set_xml(self, xmldoc):
		self.value = {}
		if xmldoc.hasChildNodes():
			for child in xmldoc.childNodes:
				if child.nodeType==1: # ELEMENT_NODE
					# For hashes with broken names with extend the xml
					if child.tagName=='_item':
						name  = child.getAttribute('name')
						if name:
							self.value[name] = XMLChild(
								child,
								parent = self,
							)
					else:
						self.value[child.tagName] = XMLChild(
							child,
							parent = self,
						)


	def get_xml(self, doc, name):

		root = doc.createElement(name)

		if not self._filename or doc.filename==self._filename:
			for key in self.keys():
				if not key.isalnum() or key[0].isdigit():
					element = self[key].get_xml(doc, '_item')
					element.setAttribute('name', key)
				else:
					element = self[key].get_xml(doc, key)
				
				if isinstance(element, minidom.Element):
					root.appendChild(element)
		elif self.filename() and doc.filename != self.filename() and self.parent():
			root.setAttribute('file', self.filename())
			# Reafirm connection with parent
			self.parent().addSubFile(self.filename(), self)
		return root

	def default(self):
		return {}

	def set(self, value):
		self.value = {}
		# Make sure data comming in is objectified
		for name in value.keys():
			self.value[name] = NChild(
				value[name],
				parent  = self,
			)

	def keys(self):
		return self.get().keys()

	def values(self):
		return self.get().values()

	def update(self, hash2):
		return self.get().update( hash2 )

	def has_key(self, name):
		return self.get().has_key(str(name))

	def __getitem__(self, name):
		if self.get().has_key(str(name)):
		    return self.get()[str(name)]

	def __setitem__(self, name, value):
		self.hasChanged()
		self.get()[str(name)] = NChild(
			value,
			parent = self,
		)

	def __delitem__(self, name):
		if self.get().has_key(name):
			self.hasChanged()
			del self.get()[name]

	def __str__(self):
		return self.to_xml()

	def children(self):
		return self.values()

class Array(Base, list):
	def set_attributes(self, xmldoc):
		if xmldoc.getAttribute('array') and not hasattr(self, '_name'):
			self._name = xmldoc.getAttribute('array')
	
	def set_xml(self, xmldoc):
		result = []
		if xmldoc.hasChildNodes():
			for child in xmldoc.childNodes:
				if child.nodeType==1: # ELEMENT_NODE
					if child.tagName==self.name():
						result.append(XMLChild(
							child,
							parent = self,
						))
		self.set(result)
	
	def get_xml(self, doc, name):
		root = doc.createElement(name)
		root.setAttribute('array', self.name())
		if not self._filename or doc.filename==self._filename:
			for value in self.get():
				element = value.get_xml(doc, self.name())
				if isinstance(element, minidom.Element):
					root.appendChild(element)
		elif self.filename() and doc.filename != self.filename():
			root.setAttribute('file', self.filename())
			self.parent().addSubFile(self.filename(), self)
		return root

	def default(self):
		return []

	def set(self, value):
		self.value = []
		# Make sure data comming in is objectified
		for child in value:
			self.value.append(NChild(
				child,
				parent = self,
			))

	def name(self):
		if not hasattr(self, '_name'):
			self._name = 'item'
		return self._name
	
	def append(self, item):
		self.hasChanged()
		child = NChild(
			item,
			parent = self,
		)
		self.get().append(child)
		return child
	
	def __getitem__(self, index):
		if index <= len(self.get()):
			return self.get()[index]

	def __setitem__(self, index, value):
		self.hasChanged()
		self.get()[index] = NChild(
			value,
			parent = self,
		)

	def __delitem__(self, index):
		if index < len(self.get()):
			self.hasChanged()
			del self.get()[index]

	def __iter__(self):
		return self.get().__iter__()

	def __len__(self):
		if not hasattr(self, 'value'):
			return 0
		return len(self.get())

	def __str__(self):
		return self.to_xml()

	def children(self):
		return self.get()

class ValueBase(Base):
	def __new__(cls, data, **options):
		return Base.__new__(cls, data, **options)

	def __init__(self, value, **options):
		self.encoded = None
		self.decoded = None
		self.value   = None
		Base.__init__(self, value, **options)

	def set_xml(self, xmldoc):
		#return self.set(self.get_xml_text(xmldoc))
		result = ''
		if xmldoc.hasChildNodes():
			for child in xmldoc.childNodes:
				if child.nodeType==3: # TEXT_NODE
					result = result + child.data
		return self.set(result)

	def get_xml(self, doc, name, ignoreType=0):
		root = doc.createElement(name)

		if ignoreType == 0:
			root.setAttribute('type', self.type())

		value = self.get()
		if not self._filename:
			root.appendChild(doc.createTextNode(str(value)))
		else:
			root.setAttribute('file', self._filename)
			self._save_me()
		return root

	def _save_me(self):
		self.save()

	def default(self):
		return ''

	def save(self):
		if self._filename and self._loaded:
			self.manager().save(self._filename, self.get())

	def load(self):
		file = self.manager().load(self._filename)
		if file:
			self._loaded = 1
			self.set(file)

	def __len__(self):
		return len(self.get())

	def __float__(self):
		return float(self.get())

# This _should_ also inherit from str or unicode, but
# can't, currently causes errors with __new__ needs more
# experenced developer to figure out.
class ValueString(ValueBase):
	def __new__(cls, data, **options):
		return ValueBase.__new__(cls, data, **options)

	def __init__(self, data, **options):
		return ValueBase.__init__(self, data, **options)

	def set(self, value):
		if value is not None:
			self.value = str(value)

	def type(self):
		return 'string'

	def __str__(self):
		return str(self.get())

	def lower(self):
		return str(self.get()).lower()


class ValueLanguage(ValueBase):
	def __init__(self, value, **options):
		self.flipSet = None
		return ValueBase.__init__(self, value, **options)

	def set(self, value):
		lang = self.currentLanguage()[0]
		return self.setLanguage(lang, value)

	def get(self):
		return self.language(self.currentLanguage())

	def language(self, langs):

		for lang in langs:
			lang = lang.lower()
			if self.value.has_key(lang):
				return self.value[lang]
			elif len(lang) == 5:
				suplang = lang[0] + lang[1]
				if self.value.has_key(suplang):
					return self.value[suplang]

		default = self.defaultLanguage()
		if self.value.has_key(default):
			return self.value[default];
		return None

	def setLanguage(self, lang, value):
		lang = lang.lower()

		if not self.value:
			self.value = {}

		if len(lang) == 5:
			suplang = lang[0] + lang[1]
			if not self.value.has_key(suplang):
				# Update the super varient, because anything is better than nothing
				self.value[suplang] = value

		self.value[lang] = value;

	def defaultLanguage(self):
		return 'en'

	def currentLanguage(self):
		lang = [ self.defaultLanguage() ]
		if self.flipSet:
			lang = [ self.flipSet ]
			self.flipSet = None
		else:
			# There is a tos up between getpreferredencoding()  and getdefaultlocale(), some say the first is better
			return locale.getdefaultlocale()
		return lang

	def type(self):
		return 'language'

	def set_xml(self, xmldoc):
		if xmldoc.hasChildNodes():
			for child in xmldoc.childNodes:
				if child.nodeType==1: # ELEMENT_NODE
					lang = child.tagName
					self.flipSet = lang
					ValueBase.set_xml(self, child)

	def get_xml(self, doc, name):
		root = doc.createElement(name)
		root.setAttribute('type', self.type())
		if not self._filename:
			for lang in self.value.keys():
				self.flipSet = lang.lower();
				element = ValueBase.get_xml(self, doc, lang, 1);
				root.appendChild(element);
		else:
			sys.stderr.write("Unable to save language to it's own file, not supported yet\n")
		return root


class ValueNumber(ValueBase):
	def set(self, value):
		if value is not None:
			self.value = int(value)

	def type(self):
		return 'number'

	def default(self):
		return 0

	def __add__(self, y):
		return self.get() + y
	def __sub__(self, y):
		return self.get() - y
	def __div__(self, y):
		return self.get() / y
	def __mul__(self, y):
		return self.get() * y

# I don't like this is programmed (by me) it just seems messy
class ValueBinary(ValueBase):
	def __init__(self, value, **options):
		ValueBase.__init__(self, value, **options)
		self.encoded = 'base64'

	def type(self):
		return 'binary'

	def set(self, value):
		if value:
			self.decoded = 1
			if isinstance(value, binary):
				self.value = value
			else:
				if not self.value:
					self.value = binary('')
				self.value.setbase64(value)

	def base64(self):
		return str(self.value)

	def __str__(self):
		return self.value.val

class binary:
	def __init__(self, data):
		self.val = data
		
	def __str__(self):
		return binascii.b2a_base64(str(self.val))
	
	def setbase64(self, value):
		self.val = binascii.a2b_base64(value)
		
	def __call__(self):
		return self.val

	def __len__(self):
		return len(self.val)
