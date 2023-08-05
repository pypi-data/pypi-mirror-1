from xml.dom.minidom import parse
import re

reo_attr_rep = re.compile('\\$\\{([a-zA-Z_][a-zA-Z0-9_]*)\\}')
reserved_keywords = {'commit': None, 'gen_doc': None}

def clz_name(fn):
    from os import path
    return path.basename(fn).split('.')[0]

def _check_reserved(name):
    if name.startswith('_') or reserved_keywords.has_key(name):
	raise NameError, '%s is a reserved keyword' % (name,)
    pass
    
class mez_xml(object):
    def __init__(self):
	super(mez_xml, self).__init__()
	pass
    
    def template_head(self):
	self.output_cmd_line('from mez_xml.tools import nez_web')
	self.output_cmd_line('')
	self.output_cmd_line('class %s(nez_web):' % (self.cname,))
	self.dig()
	self.output_cmd_line('def __init__(self, ofo):')
	self.dig()
	self.output_cmd_line('super(%s, self).__init__()' % (self.cname,))
	self.output_cmd_line('self.ofo = ofo')
	self.output_cmd_line('pass')
	self.back()
	self.output_cmd_line('')
	pass
    
    def template_tail(self):
	self.output_cmd_line('pass')
	self.back()
	self.output_cmd_line('')
	pass
    
    def subtree_start(self, cname):
	self.output_cmd_line('def %s(self, pdata, cdata):' % (cname))
	self.dig()
	self.output_cmd_line('def temp(data):')
	self.dig()
	self.frag_start()
	pass
    
    def subtree_stop(self, cname):
	self.frag_stop()
	self.output_cmd_line('pass')
	self.back()
	self.output_cmd_line('self._feed_subtree(temp, pdata, cdata)')
	self.output_cmd_line('pass')
	self.back()
	self.output_cmd_line('')
	pass
    
    def _expand_vars(self, data, _tp):
	mo = reo_attr_rep.search(data)
	pos = 0
	while mo:
	    if pos != mo.start():
		self.output(data[pos:mo.start()])
		pass
	    self.frag_stop()
	    name = mo.group(1)
	    subnames = name.split('.')
	    first = subnames[0]
	    self.output_cmd_line('odata = data.setdefault(\'%s\', {})' % (first))
	    for subname in subnames[1:]:
		self.output_cmd_line('odata = odata.setdefault(\'%s\', {})' % (subname))
		pass
	    self.output_cmd_line('self.ofo.write(self._esc_%s(odata))' % (_tp))
	    self.frag_start()
	    pos = mo.end()
	    for subname in subnames:
		_check_reserved(subname)
		pass
	    #if not self.all_names.has_key(name):
		#if not self.all_attrnames.has_key(name):
		#    self.travel_q.append((name, None))
		#    self.all_attrnames[name] = None
		#    pass
		#pass
	    #else:
		#raise NameError, '%s is redefined' % (name,)
	    mo = reo_attr_rep.search(data, pos)
	    pass
	self.output(data[pos:])
	pass
    
    def _expand_comm(self, data):
	self._expand_vars(data, 'comm')
	pass
    
    def _expand_param(self, data):
	self._expand_vars(data, 'param')
	pass
    
    def _expand_text(self, data,):
	self._expand_vars(data, 'text')
	pass
    
    def _expand_cdata(self, data):
	self._expand_vars(data, 'cdata')
	pass
    
    def gen_attrs(self, attrs):
	for i in range(attrs.length):
	    attr = attrs.item(i)
	    self.output(' ' + attr.name)
	    val = attr.nodeValue
	    if val:
		self.output('="')
		self._expand_param(val)
		self.output('"')
		pass
	    pass
	pass
    
    def tag_start(self, no):
	from xml.dom import Node
	nt = no.nodeType
	if nt == Node.CDATA_SECTION_NODE:
	    self.output('<![CDATA[')
	    self._expand_cdata(no.data)
	    self.output(']]>')
	elif nt == Node.COMMENT_NODE:
	    self.output('<!--')
	    self._expand_comm(no.data);
	    self.output('-->')
	elif nt == Node.TEXT_NODE:
	    self._expand_text(no.data);
	elif nt == Node.ELEMENT_NODE:
	    self.output('<' + no.tagName)
	    self.gen_attrs(no.attributes)
	    self.output('>')
	pass
    
    def tag_stop(self, no):
	from xml.dom import Node
	nt = no.nodeType
	if nt == Node.ELEMENT_NODE:
	    self.output('</%s>' % (no.tagName,))
	    pass
	pass
    
    def frag_start(self):
	self.output_cmd('self.ofo.write(\'\'\'')
	pass
    
    def frag_stop(self):
	self.output_raw('\'\'\')\n')
	pass
    
    def call_subtree(self, no):
	name = no.getAttribute('ezid')
	self.frag_stop()
	subnames = name.split('.')
	first = subnames[0]
	self.output_cmd_line('cdata = data.setdefault(\'%s\', {})' % (first))
	for subname in subnames[1:]:
	    self.output_cmd_line('cdata = cdata.setdefault(\'%s\', {})' % (subname))
	    pass
	last = subnames[-1]
	self.output_cmd_line('self.%s(data, cdata)' % (last))
	self.frag_start()
	pass
    
    def gen_node_template(self, name, node):
	from xml.dom import Node
	fw_q = [node]
	
	def trackback(no):
	    while no != node and no.parentNode and not no.nextSibling:
		no = no.parentNode
		self.tag_stop(no)
		pass
	    pass
	
	first = True
	while fw_q:
	    no = fw_q.pop()
	    if (not first) and no.nodeType == Node.ELEMENT_NODE and no.hasAttributes() and no.hasAttribute('ezid'):
		name = no.getAttribute('ezid').split('.')[-1]
		_check_reserved(name)
		if not self.all_names.has_key(name) and not self.all_attrnames.has_key(name):
		    self.travel_q.append((name, no))
		    self.all_names[name] = None
		else:
		    raise NameError, '%s is redefined' % (name,)
		self.call_subtree(no)
		trackback(no)
	    else:
		self.tag_start(no)
		if not no.hasChildNodes():
		    self.tag_stop(no)
		    trackback(no)
		else:
		    children = [no.childNodes.item(i) for i in range(no.childNodes.length)]
		    children.reverse()
		    fw_q.extend(children)
		    pass
		pass
	    first = False
	    pass
	pass
    
    def dig(self):
	self.indent = self.indent + 4
	pass
    
    def back(self):
	self.indent = self.indent - 4
	pass
    
    def output_cmd(self, msg):
	self.ofo.write(' ' * self.indent)
	self.ofo.write(msg)
	pass
    
    def output_cmd_line(self, msg):
	self.ofo.write(' ' * self.indent)
	self.ofo.write(msg)
	self.ofo.write('\n')
	pass

    def output_raw(self, msg):
        self.ofo.write(msg)
        pass
    
    def output(self, msg):
        parts = msg.split('\\')
        if len(parts) > 0:
            msg = '\\\\'.join(parts)
            pass
        if len(msg) > 0 and msg[-1] == '\'':
            msg = msg[:-1] + '\\\''
            pass
        parts = msg.split('\'\'\'')
        if len(parts) > 1:
            msg = '\\\'\\\'\\\''.join(parts)
            pass
	self.ofo.write(msg)
	pass
    
    def start(self, fn, ifo, ofo):
	self.ofo = ofo
	self.indent = 0
	
	cname = clz_name(fn)
	dom = parse(ifo)
	self.travel_q = [('_root', dom)]
	self.cname = cname
	self.all_names = {}
	self.all_attrnames = {}
	
	self.travel_tree()
	pass
    
    def travel_tree(self):
	self.template_head()
	
	travel_q = self.travel_q
	while travel_q:
	    name, node = travel_q[0]
	    self.subtree_start(name)
	    del travel_q[0]
	    if node:
		self.gen_node_template(name, node)
		pass
	    self.subtree_stop(name)
	    pass
	
	self.template_tail()
	pass
    pass

if __name__ == '__main__':
    import sys
    import locale
    
    if len(sys.argv) != 2:
	sys.exit(1)
	pass
    
    class fakefile(object):
	pass
    
    fn = sys.argv[1]
    fo = file(fn, 'r')
    encoding = locale.getpreferredencoding()
    stdout = fakefile()
    oldwrite = sys.stdout.write
    stdout.write = lambda x: oldwrite(x.encode(encoding))
    
    if encoding != 'ascii':
	print >> stdout, '# -*- coding: %s' % (encoding,)
	pass
    
    mex = mez_xml()
    mex.start(fn, fo, stdout)
    pass
