#!/usr/bin/env python

from copy import copy 
from HTMLParser import HTMLParser

class SearchableMixin(object):
	def __init__(self):
		self._tag_cache = {}
		self._attr_cache = {}

	def get_element_by_id(self, id):
		''' Returns the first HTMLElement that matches id '''
		elems = self.get_elements_by_id(id)
			
		if elems:
			return elems[0]

	def get_elements_by_id(self, id):
		''' Returns a list of HTMLElements that match id '''
		if id in self.id_cache:
			elems =  self.id_cache[id]
			return elems
		else:
			return []

	def get_elements_by_class_and_tag(self, classname, tagname):
		''' Returns a list of HTMLElements that both have the class classname and are of tag tagname '''
		if classname in self.class_cache:
			class_elems = set(self.class_cache[classname])
		else:
			return []
		if tagname in self.tag_cache:
			tag_elems = set(self.tag_cache[tagname])
		else:
			return []

		elems = class_elems.intersection(tag_elems)
		return list(elems)
		
	def get_element_by_class_and_tag(self, classname, tagname):
		''' Returns the first HTMLElement that has both the class classname and is of tag tagname '''
		elems = self.get_elements_by_class_and_tag(classname, tagname)
		if elems:
			return elems[0]
		else:
			return []

	def get_elements_by_class(self, classname):
		''' Returns all HTMLElements that match class classname '''
		if classname in self.class_cache:
			elems = self.class_cache[classname]
		if elems:
			return elems
		else:
			return []

	def get_element_by_class(self, classname):
		''' Returns the first HTMLElement that matches class classname '''
		elems = self.get_elements_by_class(classname)
		if elems:
			return elems[0]

	def get_elements_by_tag(self, tagname):
		''' Returns a list of HTMLElements that match the tag tagname '''
		if tagname in self.tag_cache:
			return self.tag_cache[tagname]
		else:
			return []

	def get_element_by_tag(self, tagname):
		''' Returns the first HTMLElement that matches the tag tagname '''
		elems = self.get_elements_by_tag(tagname)
		if elems:
			return elems[0]

	def get_elements_by_attr(self, attr):
		''' Returns a list of HTMLElements that have the attribute attr '''
		if attr in self.attr_cache:
			elems = []
			for a in self.attr_cache[attr].values():
				elems.extend(a)
			return elems
		else:
			return []

	def get_element_by_attr(self, attr):
		''' Returns the first HTMLElement that has the attribute attr '''
		elems = self.get_elements_by_attr(attr)
		if elems:
			return elems[0]

	def get_elements_by_attr_with_value(self, attr, val):
		''' Returns a list of HTMLElements that have the attribute attr with value val '''
		if attr in self.attr_cache and val in self.attr_cache[attr]:
			return self.attr_cache[attr][val]

	def get_element_by_attr_with_value(self, attr, val):
		''' Returns the first HTMLElement that has the attribute attr with value val '''
		elems = self.get_elements_by_attr_with_value(attr, val)
		if elems:
			return elems[0]

	def _node_cache(self):
		def _walk_children(node, attr_cache={}, tag_cache={}):
			if node.tag in tag_cache:
				tag_cache[node.tag].append(node)
			else:
				tag_cache[node.tag] = [node]
			for k,v in node._attrs.iteritems():
				if k in attr_cache:
					if v in attr_cache[k]:
						attr_cache[k][v].append(node)
					else:
						attr_cache[k][v] = [node]
				else:
					attr_cache[k] = {}
					attr_cache[k][v] = [node]
			for a in node.children:
				if isinstance(a, HTMLElement):
					attr_cache, tag_cache = _walk_children(a, attr_cache, tag_cache)
			return (attr_cache, tag_cache)

		(self._attr_cache, self._tag_cache) = _walk_children(self)

	@property
	def attr_cache(self):
		if not self._attr_cache:
			self._node_cache()

		return self._attr_cache

	@property
	def tag_cache(self):
		if not self._tag_cache:
			self._node_cache()
		
		return self._tag_cache

	@property
	def id_cache(self):
		return self.attr_cache['id']

	@property
	def class_cache(self):
		return self.attr_cache['class']

class HTMLElement(SearchableMixin):
	def __init__(self, tagname, attrs, parent=None):
		''' Initializes an HTMLElement with tag tagname, attributes attrs, and parent node parent '''
		super(HTMLElement, self).__init__()
		self._tag = tagname
		self._attrs = attrs
		self._parent = parent
		self._inner_html = ''
		self._doctype = ''
		self.children = []

	def __repr__(self):
		attrs = ', '.join([ "%s=%s" % (k,v) for k,v in self._attrs.iteritems() ])
		if attrs:
			return "<HTMLElement %s: %s>" % (self.tag, attrs)
		else:
			return "<HTMLElement %s>" % self.tag

	def __str__(self):
		return self.to_html()

	def __getitem__(self, attr):
		''' Returns an attribute of the element '''
		return self._attrs[attr]

	def __setitem__(self, attr, val):
		''' Sets an attribute of the element '''
		self._attrs[attr] = val
		self._walk_parent_nodes(lambda x: setattr(x, '_attr_cache', {}))

	def __delitem__(self, attr):
		''' Deletes an attribute of the node '''
		del self._attrs[attr]
		self._walk_parent_nodes(lambda x: setattr(x, '_attr_cache', {}))

	def __contains__(self, attr):
		''' Checks if an element includes an attribute '''
		return attr in self._attrs

	def __iadd__(self, elem):
		''' Appends a child to the node '''
		self.append_child(elem)

	def append_child(self, elem):
		''' Appends a child to the node, removing it from its parent if it has one '''
		self.children.append(elem)
		# this is potentially contestable.. If a search operation is done before the
		# parent has been changed this could cause issues.

		if elem.parent:
			elem.parent.remove_child(elem, False)
		elem._parent = self
		self._walk_parent_nodes(lambda x: setattr(x, '_tag_cache', {}))
		self._walk_parent_nodes(lambda x: setattr(x, '_attr_cache', {}))

	def remove(self):
		''' Remove node and all of its children '''
		self.parent.remove_child(self, False)
		for a in self.children:
			a.remove()

	def remove_child(self, elem, walk_children=True):
		''' Removes a child of the node, and all of its children in walk_children is True '''
		if elem.parent and elem in elem.parent.children:
			elem.parent.children.remove(elem)
			elem._walk_parent_nodes(lambda x: setattr(x, '_attr_cache', {}))
			elem._walk_parent_nodes(lambda x: setattr(x, '_tag_cache', {}))
		if walk_children:
			for a in elem.children:
				elem.remove()

	def clone(self, parent=None):
		''' Returns a clone of this HTMLElement '''
		attr_copy = copy(self._attrs)
		tag_copy = self.tag
		elem_copy = HTMLElement(tag_copy, attr_copy, parent)
		elem_copy.children = [ a.clone(elem_copy) for a in self.children ]
		return elem_copy

	def replace(self, replacement):
		''' Replace node with the node supplied in replacement '''
		replacement._parent = self.parent
		self.parent.children[self.parent.children.index(self)] = replacement
		self._walk_parent_nodes(lambda x: setattr(x, '_attr_cache', {}))
		self._walk_parent_nodes(lambda x: setattr(x, '_tag_cache', {}))
		del self

	def to_html(self, walk_children=True):
		''' Returns this HTMLElement and its children represented as HTML '''
		ret = ''
		if self._doctype:
			ret += '<!%s>' % self._doctype
		attrs = ' '.join([ "%s='%s'" %(k, v) for k,v in self._attrs.iteritems() ])
		if walk_children:
			child = ''.join([ a.to_html() for a in self.children ])
		else:
			child = ''
		if attrs:
			return str(ret+'<%s %s>%s</%s>' % (self.tag, attrs, child, self.tag))
		else:
			return str(ret+'<%s>%s</%s>' % (self.tag, child, self.tag))

	def _walk_parent_nodes(self, func):
		''' Walks up the parent tree calling func on each parent node '''
		node = self
		while node:
			func(node)
			node = node.parent

	def _get_inner_html(self):
		return "%s" % ''.join([a.to_html() for a in self.children])

	def _set_inner_html(self, html_str):
		wrapped = "<div>%s</div>" % html_str
		top_div = StringKiln(wrapped)
		for a in self.children:
			del a
		self.children = top_div.children
		for a in self.children:
			a._parent = self

		self._walk_parent_nodes(lambda x: setattr(x, '_attr_cache', {}))
		self._walk_parent_nodes(lambda x: setattr(x, '_tag_cache', {}))

	def _get_id(self):
		if 'id' in self._attrs:
			return self['id']
		else:
			return None

	def _set_id(self, val):
		if isinstance(val, basestring):
			self['id'] = val
		elif val is None:
			del self['id']

	def _set_tag(self, val):
		self._tag = val
		self._walk_parent_nodes(lambda x: setattr(x, '_tag_cache', {}))

	def _set_parent(self, parent):
		parent.append_child(self)

	id = property(_get_id, _set_id)
	inner_html = property(_get_inner_html, _set_inner_html)
	tag = property(lambda x: x._tag, _set_tag)
	parent = property(lambda x: x._parent, _set_parent)

class DataElement(object):
	def __init__(self, content, parent=None):
		''' Initalizes a DataElement containing the string content '''
		self.content = content
		self.parent = parent

	def to_html(self, walk_children=None):
		''' Returns an HTML representation of the DataElement for use by HTMLElement '''
		return self.content.encode('utf-8')

	def remove(self):
		self.parent.children.remove(self)

	def clone(self, parent=None):
		''' Clones the DataElement '''
		return DataElement(self.content, parent)

	def __repr__(self):
		return "<DataElement>"

	def __str__(self):
		return str(self.content)

class _ParseMan(HTMLParser, object):
	def __init__(self):
		super(_ParseMan, self).__init__()
		self.open_stack = []
		self.head = None
		self.doctype = None

	def handle_starttag(self, tag, attrs):
		if self.open_stack:
			parent = self.open_stack[-1]
		else:
			parent = None

		attr_dict = {}
		for k,v in attrs:
			attr_dict[k] = v

		element = HTMLElement(tag, attr_dict, parent)
		if parent:
			parent.children.append(element)
		else:
			self.head = element
		if tag.lower() not in ['link', 'meta']:
			self.open_stack.append(element)
		if tag.lower() == 'html' and self.doctype:
			element._doctype = self.doctype

	def handle_startendtag(self, tag, attrs):
		if self.open_stack:
			parent = self.open_stack[-1]
		else:
			parent = None

		attr_dict = {}
		for k,v in attrs:
			attr_dict[k] = v

		element = HTMLElement(tag, attr_dict, parent)
		if parent:
			parent.children.append(element)
		else:
			self.head = element
			
	def handle_endtag(self, tag):
		self.open_stack.pop()

	def handle_data(self, data):
		if self.open_stack:
			parent = self.open_stack[-1]
			parent.children.append(DataElement(data, parent))

	def handle_decl(self, data):
		if data.startswith('DOCTYPE'):
			self.doctype = data

def FileKiln(filename_or_obj):
	''' Takes a file (either name or object) as input and returns the parent HTMLElement '''
	if isinstance(filename_or_obj, basestring):
		file_obj = open(filename_or_obj)
	elif isinstance(filename_or_obj, file):
		file_obj = filename_or_obj
	else:
		raise Exception('Input object neither filename nor file object')
	parser = _ParseMan()
	parser.feed(file_obj.read())
	return parser.head

def StringKiln(html_string):
	''' Takes an HTML string as input and returns the HTMLElement in the string '''
	parser = _ParseMan()
	parser.feed(html_string)
	return parser.head
