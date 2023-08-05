#!/usr/local/bin/python
from xml.sax import make_parser
from xml.sax.handler import ContentHandler, feature_validation, feature_external_ges, feature_external_pes
from xml.sax.saxutils import prepare_input_source

def get_attr_str(attrs):
    from string import join
    names = attrs.getNames()
    attr_strs = ['["' + name + '","' + attrs.getValue(name) + '"]' for name in names if not ':' in name]
    return '[' + join(attr_strs, ',') + ']'

class xhtml2js_handler(ContentHandler):
    def __init__(self, xhtml_name):
	ContentHandler.__init__(self)
	self.xhtml_name = xhtml_name
	self.in_body = False
	pass
    
    def startDocument(self):
	print 'function %s() {' % (self.xhtml_name)
	print '\tvar top, content = new Object();'
	print '\tvar stk = new Array();'
	print '\tvar add = function(n, attrs) {'
	print '\t\tvar i, o = new_elm(n);'
	print '\t\tfor(i = 0; i < attrs.length; i++) {'
	print '\t\t\tif(attrs[i][0] == "id") eval("content." + attrs[i][1] + "=o");'
	print '\t\t\telse o.setAttribute(attrs[i][0], attrs[i][1]);'
	print '\t\t}'
	print '\t\tstk[stk.length-1].appendChild(o);'
	print '\t\tstk.push(o);'
	print '\t}'
	print '\tvar txt = function(str) {'
	print '\t\tvar o = new_text(str);'
	print '\t\tstk[stk.length - 1].appendChild(o);'
	print '\t}'
	print
	print '\ttop = new_elm("div");'
	print '\tstk.push(top);'
	print
	pass
    
    def endDocument(self):
	print
	print '\ttop.xhtml_content = content;'
	print '\treturn top;'
	print '}'
	pass
    
    def startElement(self, name, attrs):
	if not self.in_body:
	    if name.lower() == 'body':
		self.in_body = True
		pass
	    return
	
	self.open_node(name, attrs)
	pass
    
    def endElement(self, name):
	if not self.in_body:
	    return
	if name.lower() == 'body':
	    self.in_body = False
	    return
	
	self.close_node(name)
	pass
    
    def open_node(self, name, attrs):
	attr_str = get_attr_str(attrs)
	print '\tadd("%s", %s);' % (name, attr_str)
	pass
    
    def close_node(self, name):
	print '\tstk.pop();'
	pass
    
    def characters(self, content):
	if not self.in_body:
	    return
	if not content.isspace():
	    print '\ttxt("%s");' % (content)
	    pass
	pass
    pass

if __name__ == '__main__':
    from sys import argv

    def filename_to_scriptname(name):
        from os.path import basename
        from string import maketrans
        name = basename(name)
        trans = maketrans('-$ ', '___')
        r = 'xhtml_' + name.split('.')[0].translate(trans)
        return r

    fn=argv[1]
    fo = file(fn)
    
    parser = make_parser()
    parser.setFeature(feature_validation, False);
    parser.setFeature(feature_external_ges, False);
    parser.setFeature(feature_external_pes, False);
    handler = xhtml2js_handler(filename_to_scriptname(fn));
    parser.setContentHandler(handler)
    parser.parse(prepare_input_source(fo))
    pass

