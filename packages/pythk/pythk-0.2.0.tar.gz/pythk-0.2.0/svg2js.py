#!/usr/local/bin/python
from xml.sax import make_parser
from xml.sax.handler import ContentHandler, feature_validation, feature_external_ges, feature_external_pes
from xml.sax.saxutils import prepare_input_source

def svg_elm_script(name, attr_str):
    return '\tadd("%s", %s);' % (name, attr_str)

def get_attr_str(attrs):
    from string import join
    names = attrs.getNames()
    attr_strs = ['["' + name + '","' + attrs.getValue(name) + '"]' for name in names if not ':' in name]
    return '[' + join(attr_strs, ',') + ']'

class svg2js_handler(ContentHandler):
    handle_tags = ('svg', 'g', 'line', 'path', 'rect', \
    'defs', 'marker', 'linearGradient', 'stop', 'text', \
    'tspan')
    
    def __init__(self, gn):
        ContentHandler.__init__(self)
        self.gn = gn
	self.ignore = 0
	self.lines = []
        pass
    
    def output(self, line):
	self.lines.append(line)
	pass
    
    def get_output_str(self):
	import string
	return string.join(self.lines, '\n') + '\n'
    
    def startDocument(self):
	output = self.output
        output('function %s() {' % (self.gn))
        output('\tvar top, svg_content = new Object();')
        output('\tvar a = new Array();')
        output('\tvar add = function(name, attrs) {')
        output('\t\tvar i, o = new_svg_elm(name);')
        output('\t\tfor(i = 0; i < attrs.length; i++) {')
        output('\t\t\tif(attrs[i][0] == "id") eval("svg_content." + attrs[i][1] + " = o");')
        output('\t\t\to.setAttribute(attrs[i][0], attrs[i][1]);')
        output('\t\t}')
        output('\t\ta[a.length - 1].appendChild(o);')
        output('\t\ta.push(o);')
        output('\t}')
	output('\tvar txt = function(str) {')
	output('\t\tvar o = new_text(str);')
	output('\t\ta[a.length - 1].appendChild(o);')
	output('\t}')
        output('')
        output('\ttop = new_elm("div");')
        output('\ttop.style.margin = "0";')
        output('\ttop.style.padding = "0";')
        output('\ta.push(top);')
        output('')
        pass
    
    def endDocument(self):
        output = self.output
	output('')
        output('\ttop.svg_content = svg_content;')
        output('\treturn top;')
        output('}')
        pass
    
    def startElement(self, name, attrs):
	if self.ignore > 0:
	    self.ignore = self.ignore + 1
	    return
        if name in self.handle_tags:
            self.output(svg_elm_script(name, get_attr_str(attrs)))
	else:
	    self.ignore = self.ignore + 1
            pass
        pass
    
    def endElement(self, name):
	if self.ignore > 0:
	    self.ignore = self.ignore - 1
	    return
        if name in self.handle_tags:
	    self.output('\ta.pop();')
            pass
        pass
    
    def characters(self, content):
	if self.ignore > 0:
	    return
	if not content.isspace():
	    self.output('\ttxt("%s");' % (content))
	    pass
	pass
    pass


def filename_to_scriptname(name):
    from os.path import basename
    from string import maketrans
    name = basename(name)
    trans = maketrans('-$ ', '___')
    r = 'svg_' + name.split('.')[0].translate(trans)
    return r


def svg2js_in_src(src, name):
    parser = make_parser()
    parser.setFeature(feature_validation, False);
    parser.setFeature(feature_external_ges, False);
    parser.setFeature(feature_external_pes, False);
    handler = svg2js_handler(filename_to_scriptname(name));
    parser.setContentHandler(handler)
    parser.parse(src)
    return handler.get_output_str()


def svg2js_str(svg_str, name):
    from StringIO import StringIO
    return svg2js_file(StringIO(svg_str), name)


def svg2js_file(svg_file, name):
    if not getattr(svg_file, 'read'): raise TypeError()
    src = prepare_input_source(svg_file)
    return svg2js_in_src(src, name)


if __name__ == '__main__':
    from sys import argv, stdout

    fn=argv[1]
    fo = file(fn)
    
    stdout.write(svg2js_file(fo, fn))
    pass



