# python modules
import sys, os

# zope modules
from zope.security.proxy import removeSecurityProxy


def flatten(inlist, ltype=(list, tuple)):
	"""Flatten a list.

	@param inlist list to expant
	@param ltype types of sequences to expand

	>>> flatten([1, 2, (3, 4, [5, 6], 7), 8, 9])
	[1, 2, 3, 4, 5, 6, 7, 8, 9]
	"""

	try:
		# for every possible index
		for ind in xrange(sys.maxint):
			# while that index currently holds a list
			while isinstance(inlist[ind], ltype):
				# expand that list into the index (and subsequent indicies)
				inlist[ind:ind+1] = list(inlist[ind])
	except IndexError:
		pass
	return inlist


def split_len(seq, length):
	"""Split sequence into groups of 'length'.


	>>> split_len([1,2,3,4,5,6,7,8], 3)
	[[1, 2, 3], [4, 5, 6], [7, 8]]
	"""

	return [seq[i:i+length] for i in range(0, len(seq), length)]


def logged(call):
	"""Logging wrapper.

		>>> @logged
		... def sum(x, y):
		...		return x + y

		>>> sum(1,2) #doctest:+ELLIPSIS
		Call <function sum at ...>(1, 2){}
		<function sum at ...> Resulted 3
		3

	"""

	def wrapped(*args, **kargs):
		print "Call " + str(call) + str(args).encode('utf-8') + str(kargs).encode('utf-8')
		result = call(*args, **kargs)
		print str(call) + " Resulted " + str(result).encode('utf-8')
		return result
	return wrapped


def splitext(name):
	"""Split file name to base name and extension.

	NOTE: This is different from os.path.splitext in that the extension does not have an extension separator prefixed, and it handles hidden files correctly.

	Examples:

		>>> splitext(u'document.txt')
		(u'document', u'txt')

	Unicode strings are returned regardless of the input:

		>>> splitext('file')
		(u'file', u'')

	In hidden files the first dot is ignored:

		>>> splitext(u'.hidden')
		(u'hidden', u'')
	"""

	if name[0] == '.':
		name = name[1:]
	(base, ext) = os.path.splitext(name)
	if len(ext) > 0: ext = ext[1:]
	return (unicode(base), unicode(ext))


def getClassFullName(cls):
	"""Get full name of class from class.

	Example:
		>>> from jz.testing.sample import Content

		get the classes's name:
		>>> getClassFullName(Content)
		u'jz.testing.sample.Content'

		if a non-class object is passed, a ValueError is raised:
		>>> a = 1
		>>> getClassFullName(a)
		Traceback (most recent call last):
		...
		ValueError

	"""

	try:
		result = u"%s.%s" % (cls.__module__, cls.__name__,)
	except:
		raise ValueError
	return result


def getClassName(cls):
	"""Get class name from class.

	Exapmle:
		>>> from jz.testing.sample import Content

		get the classes's name:
		>>> getClassName(Content)
		u'Content'
	"""

	return getClassFullName(cls).split('.')[-1]


def getObjectClassFullName(object):
	"""Get class full name from object.

	Example:
		>>> from jz.testing.sample import Content
		>>> sample = Content()

	the class string representation is:
	 	>>> str(sample.__class__)
		"<class 'jz.testing.sample.Content'>"

	and this function returns only the name:
	 	>>> getObjectClassFullName(sample)
		u'jz.testing.sample.Content'

	another example with the actual class passed as an object
		>>> getObjectClassFullName(Content)
		u'type'

	"""

	result = unicode(object.__class__).split(' ')[-1][1:]
	# addition for new style class str representation
	if result[-2:] == "'>":
		result = result[:-2]
	return result


def getObjectClassName(object):
	"""Get class name from object without full module path.

	Example:
		>>> from jz.testing.sample import Content
		>>> sample = Content()

	the full class name is:
		>>> str(sample.__class__)
		"<class 'jz.testing.sample.Content'>"

	and this function returns only the last element in that path:
		>>> getObjectClassName(sample)
		u'Content'

	"""

	result = getObjectClassFullName(object).split('.')[-1]
	return result


class SimpleAdapter(object):
	"""Base class for adapter of single object.

	Example:

		>>> c = object()

		>>> adapter = SimpleAdapter(c)
		>>> adapter.context is c
		True

	"""

	def __init__(self, context):
		self.context = context


def removeAllAdapters(context):
	"""Remove all adapters.

	Test for adapter by presence of context attribute.

		>>> class Content(object):
		...		name = "source"

		>>> class Adapter(object):
		...		def __init__(self, context):
		...			self.context = context
		...			self.name = "adapter"

		>>> c = Content()
		>>> a = Adapter(c)
		>>> a.name
		'adapter'

		>>> removeAllAdapters(a).name
		'source'
	"""

	obj = removeSecurityProxy(context)
	if hasattr(obj, "context"):
		return removeAllAdapters(obj.context)
	return context
