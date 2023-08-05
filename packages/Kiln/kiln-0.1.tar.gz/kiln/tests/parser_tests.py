#!/usr/bin/env python

import sys
sys.path.append('.')
import kiln

def string_setup():
	return kiln.StringKiln('<html>\n\t<head>\n\t\t<LINK href="/static/css/base.css" rel="stylesheet" type="text/css">\n\t\t<script src="/static/js/MochiKit.js"></script>\n\t</head>\n\t<body onload="startup()">\n\t\t<div id="header">\n\t\t\t<div class="base"></div>\n\t\t\t<div id=\'title\' class="title"></div>\n\t\t</div>\n\t\t<div class="hideme"></div>\n\t\t<div id="list_entry_header">\n\t\t\t<div class="entry_image"></div>\n\t\t\t<span class="entry_name"><nobr>name</nobr></span>\n\t\t\t<span class="entry_date">date</span>\n\t\t\t<div class="entry_size"><nobr>size</nobr></div>\n\t\t</div>\n\t\t<div id="container">\n\t\t</div>\n\t\t<div id="list_options"><input type="checkbox" id="single_expand" />Collapse sections automatically</div>\n\t</body>\n</html>\n')

def file_setup():
	return kiln.FileKiln('tests/base.html')

def check_is_html_element(head):
	''' Test that the Parser returned an HTMLElement '''
	assert isinstance(head, kiln.HTMLElement)

def check_is_html_tag(head):
	''' Test that the HTMLElement's tag is HTML '''
	assert head.tag.lower() == 'html'

def check_has_no_attrs(head):
	''' Test that the HTMLElement has no attributes '''
	assert head._attrs == {}

def check_has_five_children(head):
	''' Test that the HTMLElement has five children '''
	assert len(head.children) == 5

def check_first_child_is_data_element(head):
	''' Test that the first child is a DataElement '''
	assert isinstance(head.children[0], kiln.DataElement)

def test_parser_generator():
	check_methods = [ m for m in globals() if m.startswith('check_') ]
	for a in ['string_setup', 'file_setup']:
		head = globals()[a]()
		for b in check_methods:
			yield globals()[b], head
