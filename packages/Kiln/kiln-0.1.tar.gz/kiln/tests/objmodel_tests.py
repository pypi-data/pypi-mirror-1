#!/usr/bin/env python

import sys
sys.path.append('.')
import kiln

class TestObjectModel(object):
	def setup(self):
		self.head = kiln.StringKiln('<html>\n\t<head>\n\t\t<LINK href="/static/css/base.css" rel="stylesheet" type="text/css">\n\t\t<script src="/static/js/MochiKit.js"></script>\n\t</head>\n\t<body onload="startup()">\n\t\t<div id="header">\n\t\t\t<div class="base"></div>\n\t\t\t<div id=\'title\' class="title"></div>\n\t\t</div>\n\t\t<div class="hideme"></div>\n\t\t<div id="list_entry_header">\n\t\t\t<div class="entry_image"></div>\n\t\t\t<span class="entry_name"><nobr>name</nobr></span>\n\t\t\t<span class="entry_date">date</span>\n\t\t\t<div class="entry_size"><nobr>size</nobr></div>\n\t\t</div>\n\t\t<div id="container">\n\t\t</div>\n\t\t<div id="list_options"><input type="checkbox" id="single_expand" />Collapse sections automatically</div>\n\t</body>\n</html>\n')

	def test_remove_children_walk_parents(self):
		''' Make sure that a lookup of a node fails after it has been removed '''
		elem = self.head.get_element_by_tag('head')
		self.head.remove_child(elem)
		assert self.head.get_element_by_tag('head') == None

	def test_add_children_walk_parents(self):
		''' Make sure that a lookup of a node succeeds after it has been added '''
		elem = self.head.get_element_by_tag('head')
		elem.append_child(kiln.HTMLElement('h1', {}))
		assert isinstance(self.head.get_element_by_tag('h1'), kiln.HTMLElement)

	def test_change_attribute_walks_parents(self):
		''' Make sure that a lookup of a node succeeds after its attributes have been modified '''
		elem = self.head.get_element_by_id('header')
		elem['id'] = 'something_else'
		assert isinstance(self.head.get_element_by_id('something_else'), kiln.HTMLElement)

	def test_remove_children_removes_nodes_from_html(self):
		''' Make sure that the HTML representation of the tree is correct once a node has been removed '''
		elem = self.head.get_element_by_tag('head')
		self.head.remove_child(elem)
		assert str(self.head) == "<html>\n\t\n\t<body onload='startup()'>\n\t\t<div id='header'>\n\t\t\t<div class='base'></div>\n\t\t\t<div id='title' class='title'></div>\n\t\t</div>\n\t\t<div class='hideme'></div>\n\t\t<div id='list_entry_header'>\n\t\t\t<div class='entry_image'></div>\n\t\t\t<span class='entry_name'><nobr>name</nobr></span>\n\t\t\t<span class='entry_date'>date</span>\n\t\t\t<div class='entry_size'><nobr>size</nobr></div>\n\t\t</div>\n\t\t<div id='container'>\n\t\t</div>\n\t\t<div id='list_options'><input type='checkbox' id='single_expand'></input>Collapse sections automatically</div>\n\t</body>\n</html>"

	def test_add_children_adds_nodes_to_html(self):
		''' Make sure that the HTML representation of the tree is correct once a node has been added '''
		elem = self.head.get_element_by_tag('head')
		elem.append_child(kiln.HTMLElement('h1', {}))
		print repr(str(self.head))
		assert str(self.head) == "<html>\n\t<head>\n\t\t<link href='/static/css/base.css' type='text/css' rel='stylesheet'></link>\n\t\t<script src='/static/js/MochiKit.js'></script>\n\t<h1></h1></head>\n\t<body onload='startup()'>\n\t\t<div id='header'>\n\t\t\t<div class='base'></div>\n\t\t\t<div id='title' class='title'></div>\n\t\t</div>\n\t\t<div class='hideme'></div>\n\t\t<div id='list_entry_header'>\n\t\t\t<div class='entry_image'></div>\n\t\t\t<span class='entry_name'><nobr>name</nobr></span>\n\t\t\t<span class='entry_date'>date</span>\n\t\t\t<div class='entry_size'><nobr>size</nobr></div>\n\t\t</div>\n\t\t<div id='container'>\n\t\t</div>\n\t\t<div id='list_options'><input type='checkbox' id='single_expand'></input>Collapse sections automatically</div>\n\t</body>\n</html>"

	def test_change_attribute_walks_parents(self):
		''' Make sure that a lookup of a node succeeds after its attributes have been modified '''
		elem = self.head.get_element_by_id('header')
		elem['id'] = 'something_else'
		print repr(str(self.head))
		assert str(self.head) == "<html>\n\t<head>\n\t\t<link href='/static/css/base.css' type='text/css' rel='stylesheet'></link>\n\t\t<script src='/static/js/MochiKit.js'></script>\n\t</head>\n\t<body onload='startup()'>\n\t\t<div id='something_else'>\n\t\t\t<div class='base'></div>\n\t\t\t<div id='title' class='title'></div>\n\t\t</div>\n\t\t<div class='hideme'></div>\n\t\t<div id='list_entry_header'>\n\t\t\t<div class='entry_image'></div>\n\t\t\t<span class='entry_name'><nobr>name</nobr></span>\n\t\t\t<span class='entry_date'>date</span>\n\t\t\t<div class='entry_size'><nobr>size</nobr></div>\n\t\t</div>\n\t\t<div id='container'>\n\t\t</div>\n\t\t<div id='list_options'><input type='checkbox' id='single_expand'></input>Collapse sections automatically</div>\n\t</body>\n</html>"
