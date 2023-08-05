#!/usr/bin/env python

import sys
sys.path.append('.')
import kiln

class TestSearchFunctions(object):
	def setup(self):
		self.head = kiln.StringKiln('<html>\n\t<head>\n\t\t<LINK href="/static/css/base.css" rel="stylesheet" type="text/css">\n\t\t<script src="/static/js/MochiKit.js"></script>\n\t</head>\n\t<body onload="startup()">\n\t\t<div id="header">\n\t\t\t<div class="base"></div>\n\t\t\t<div id=\'title\' class="title"></div>\n\t\t</div>\n\t\t<div class="hideme"></div>\n\t\t<div id="list_entry_header">\n\t\t\t<div class="entry_image"></div>\n\t\t\t<span class="entry_name"><nobr>name</nobr></span>\n\t\t\t<span class="entry_date">date</span>\n\t\t\t<div class="entry_size"><nobr>size</nobr></div>\n\t\t</div>\n\t\t<div id="container">\n\t\t</div>\n\t\t<div id="list_options"><input type="checkbox" id="single_expand" />Collapse sections automatically</div>\n\t</body>\n</html>\n')

	def test_get_by_id(self):
		elem = self.head.get_element_by_id('single_expand')
		assert elem.tag == 'input'
		assert elem['type'] == 'checkbox'
		assert len(elem.children) == 0

	def test_get_by_tag(self):
		elem = self.head.get_element_by_tag('script')
		assert elem['src'] == '/static/js/MochiKit.js'
		assert len(elem.children) == 0

	def test_get_by_attr(self):
		elem = self.head.get_element_by_attr('onload')
		assert elem.tag == 'body'

	def test_get_by_attr_with_value(self):
		elem = self.head.get_element_by_attr_with_value('id', 'container')
		assert elem.tag == 'div'

	def test_get_by_class(self):
		elem = self.head.get_element_by_class('entry_date')
		assert elem.tag == 'span'
		assert elem.inner_html == 'date'

	def test_get_by_class_and_tag(self):
		elem = self.head.get_element_by_class_and_tag('entry_name', 'span')
		assert len(elem.children) == 1
