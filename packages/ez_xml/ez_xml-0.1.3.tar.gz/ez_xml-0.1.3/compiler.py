from xml.dom.minidom import parse
from xml import dom
import re

temp_value_reo = re.compile('\\{[0-9a-zA-Z-_/]+\\}')

def xml_to_template(in_fo, out_fo, partial):
    from xml.dom import Node
    
    def begin_text(o):
        out_fo.write(o.data.encode('utf8'))
        pass
    def end_text(o):
        pass
    
    def begin_comment(o):
        out_fo.write('<!--')
        out_fo.write(o.data.encode('utf8'))
        out_fo.write('-->')
        pass
    def end_comment(o):
        pass
    
    
    def begin_element(o):
	if o.tagName == 'FAKE':
	    return
        out_fo.write('<')
        out_fo.write(o.tagName)
        for i in range(o.attributes.length):
            attr = o.attributes.item(i)
            out_fo.write(' ')
            out_fo.write(attr.name)
            out_fo.write('="')
            if not temp_value_reo.search(attr.value):
                out_fo.write(attr.value.encode('utf8'))
            else:
                stop_frag()
                
                last = 0
                for mo in temp_value_reo.finditer(attr.value):
                    if mo.start() != last:
                        out_fo.write('\tout_fo.write(' + repr(attr.value[last:mo.start()].encode('utf8')) + ')\n')
                        pass
                    last = mo.end()
                    setup_tmpcur(mo.group()[1:-1])
                    out_fo.write('\tout_fo.write(str(tmpcur))\n')
                    pass
                if last < len(attr.value):
                    out_fo.write('\tout_fo.write(' + repr(attr.value[last:]) + ')\n')
                    pass
                
                start_frag()
                pass
            out_fo.write('"')
            pass
        if o.hasChildNodes():
            out_fo.write('>')
        else:
            out_fo.write('/>')
        pass
    def end_element(o):
	if o.tagName == 'FAKE':
	    return
        if o.hasChildNodes():
            out_fo.write('</')
            out_fo.write(o.tagName)
            out_fo.write('>')
            pass
        pass
    
    tag_actions = dict()
    tag_actions[Node.TEXT_NODE] = (begin_text, end_text)
    tag_actions[Node.COMMENT_NODE] = (begin_comment, end_comment)
    tag_actions[Node.ELEMENT_NODE] = (begin_element, end_element)
    
    def start_frag(lvl=1):
        out_fo.write('\t' * lvl)
        out_fo.write('out_fo.write(\'\'\'')
        pass
    
    def stop_frag():
        out_fo.write('\'\'\')\n')
        pass
    
    def start_func(fname, params):
        from string import join
        out_fo.write('\n')
        out_fo.write('def ' + fname + '(' + join(params, ', ') + '):\n')
        pass
    
    def stop_func():
        out_fo.write('\n')
        pass
    
    def setup_cur(data_path):
        out_fo.write('\tcur = get_cur_from_data_path(cur, out, ' + repr(data_path.encode('utf8')) + ')\n')
        pass
    
    def setup_tmpcur(data_path):
        out_fo.write('\ttmpcur = get_cur_from_data_path(cur, out, ' + repr(data_path.encode('utf8')) + ')\n')
        pass
    
    workq = []
    
    def repeat(o, data_path):
        fname = 'repeat_' + str(repeat.sn)
        repeat.sn += 1
        out_fo.write('\t')
        out_fo.write(fname + '(cur, out, out_fo)\n')
        workq.append(lambda: gen_repeat(o, data_path, fname))
        pass
    repeat.sn = 0
    
    def gen_repeat(o, data_path, fname):
        o.removeAttribute('temp_act')
        
        start_func(fname, ('cur', 'out', 'out_fo'))
        setup_cur(data_path)
        out_fo.write('\tfor i in range(len(cur)):\n')
        out_fo.write('\t\t' + fname + '_output(cur[i], out, out_fo)\n')
        stop_func()
        
        start_func(fname + '_output', ('cur', 'out', 'out_fo'))
        out_fo.write('\trepeat_patterns = []\n')
        traveler_o.travel(o)
        stop_func()
        pass
    
    class repeat_group(object):
        sn = 0
        def __init__(self, o, data_path, skip_node=False):
            self.o = o
            self.data_path = data_path
	    self.skip_node = skip_node
            fname = 'repeat_group_' + str(repeat_group.sn)
            self.fname = fname
            repeat_group.sn += 1
            self.ptn_sn = 0
            
            out_fo.write('\t' + fname + '(cur, out, out_fo)\n')
            
            workq.append(self.gen_repeat_group)
            pass
        
        def gen_repeat_group(self):
            o = self.o
	    if not self.skip_node:
		o.removeAttribute('temp_act')
	    else:
		o.setAttribute('temp_act', 'skip_node(this)')
		pass
            
            start_func(self.fname, ('cur', 'out', 'out_fo'))
            setup_cur(self.data_path)
            out_fo.write('\ti = 0\n')
            out_fo.write('\twhile i < len(cur):\n')
            out_fo.write('\t\ti = ' + self.fname + '_output(cur, out, out_fo, i)\n')
            stop_func()
            
            start_func(self.fname + '_output', ('cur', 'out', 'out_fo', 'i'))
            saved_group_pattern = temp_actions['group_pattern']
            temp_actions['group_pattern'] = self.group_pattern
            traveler_o.travel(o)
            temp_actions['group_pattern'] = saved_group_pattern
            out_fo.write('\treturn i\n')
            stop_func()
            pass
    
        def group_pattern(self, o):
            fname = 'group_pattern_' + str(self.sn) + '_' + str(self.ptn_sn)
	    self.ptn_sn += 1
            out_fo.write('\tif i < len(cur):\n')
            out_fo.write('\t\t' + fname + '(cur[i], out, out_fo)\n')
            out_fo.write('\t\ti += 1\n')
            workq.append(lambda: self.gen_group_pattern(o, fname))
            pass
        
        def gen_group_pattern(self, o, fname):
            o.removeAttribute('temp_act')
            start_func(fname, ('cur', 'out', 'out_fo'))
            traveler_o.travel(o)
            stop_func()
            pass
        pass
    
    def replace_node(path):
        setup_tmpcur(path)
        out_fo.write('\tout_fo.write(str(tmpcur))\n')
        pass
    
    def skip_node(o):
	if o.hasChildNodes():
	    for i in range(o.childNodes.length):
		traveler_o.travel(o.childNodes.item(i))
		pass
	    pass
	pass
    
    def invalid(*dummy):
        raise RuntimeError()
    
    temp_actions = {}
    temp_actions['replace_node'] = replace_node
    temp_actions['repeat'] = repeat
    temp_actions['repeat_group'] = repeat_group
    temp_actions['group_pattern'] = invalid
    temp_actions['skip_node'] = skip_node
    temp_actions['ignore'] = lambda: None
    
    def process_node(node):
        pass
    
    class traveler(object):
	def __init__(self, tag_acts, temp_acts):
	    super(traveler, self).__init__()
	    self.tag_acts = tag_acts
	    self.temp_acts = temp_acts
	    pass
	
	def go_next(self, visiting, root_node):
	    while visiting:
		end_act = self.tag_acts[visiting.nodeType][1]
		end_act(visiting)
		if visiting == root_node:
		    return None
		if visiting.nextSibling != None:
		    visiting = visiting.nextSibling
		    break
		visiting = visiting.parentNode
		pass
	    return visiting
	
	def skip_one(self, visiting, root_node):
	    if visiting == root_node:
		return None
	    if visiting.nextSibling != None:
		return visiting.nextSibling
	    visiting = visiting.parentNode
	    return self.go_next(visiting, root_node)
	
	def run_action(self, node, act_str):
	    gdict = self.temp_acts
	    ldict = {'out_fo': out_fo, 'this': node}
	    exec act_str in gdict, ldict
	    pass
    
	def travel(self, root_node):
	    visiting = root_node
	    start_frag()
	    while visiting:
		if visiting.nodeType == Node.COMMENT_NODE and (visiting.data.startswith('FAKE_BEGIN:') or visiting.data.startswith('FAKE:')):
		    fake_o = doc_o.createElement('FAKE')
		    first_colon = visiting.data.index(':')
		    fake_o.setAttribute('temp_act', visiting.data[first_colon + 1:])
		    visiting.parentNode.insertBefore(fake_o, visiting)
		    visiting.parentNode.removeChild(visiting)
		    
		    if visiting.data.startswith('FAKE_BEGIN:'):
			visiting = fake_o.nextSibling
			while visiting:
			    if visiting.nodeType == Node.COMMENT_NODE and visiting.data.startswith('FAKE_END'):
				break
			    o = visiting
			    visiting = visiting.nextSibling
			    fake_o.appendChild(o)
			    pass
			if not visiting:
			    raise SyntaxError()
			visiting.parentNode.removeChild(visiting)
			pass
		    visiting = fake_o
		    pass
		
		if visiting.nodeType == Node.ELEMENT_NODE and visiting.hasAttribute('temp_act'):
		    stop_frag()
		    act_str = visiting.getAttribute('temp_act')
		    self.run_action(visiting, act_str)
		    start_frag()
		    visiting = self.skip_one(visiting, root_node)
		    continue
		
		begin_act = self.tag_acts[visiting.nodeType][0]
		begin_act(visiting)
		if visiting.hasChildNodes():
		    visiting = visiting.childNodes.item(0)
		else:
		    visiting = self.go_next(visiting, root_node)
		    pass
		pass
	    stop_frag()
	    pass
	pass
    
    def gen_template(root_node, partial=False):
        out_fo.write('from ez_xml.tools import get_cur_from_data_path, formalize_out\n\n')
        start_func('template', ('out', 'out_fo'))
        out_fo.write('\tformalize_out(out)\n')
        out_fo.write('\tcur = out\n')
	if not partial:
	    traveler_o.travel(root_node)
	else:
	    ignore = lambda *args: None
	    tag_actions = dict()
	    tag_actions[Node.TEXT_NODE] = (ignore, ignore)
	    tag_actions[Node.COMMENT_NODE] = (ignore, ignore)
	    tag_actions[Node.ELEMENT_NODE] = (ignore, ignore)
	    def temp_root(node):
		for i in range(node.childNodes.length):
		    traveler_o.travel(node.childNodes.item(i))
		    pass
		pass
	    temp_actions = {'temp_root': temp_root}
	    h_traveler_o = traveler(tag_actions, temp_actions)
	    h_traveler_o.travel(root_node)
	    pass
        pass
    
    doc_o = parse(in_fo)
    traveler_o = traveler(tag_actions, temp_actions)
    for i in range(doc_o.childNodes.length):
        visiting = doc_o.childNodes.item(i)
        if visiting.nodeType == Node.ELEMENT_NODE:
            break
        pass
    workq.append(lambda: gen_template(visiting, partial))
    i = 0
    while i < len(workq):
        workq[i]()
        i += 1
        pass
    pass

if __name__ == '__main__':
    import sys, locale, string
    from codecs import EncodedFile
    
    def usage():
	import os.path
	bname = os.path.basename(sys.argv[0])
	print 'USAGE: %s: [-p] <XML file> > <template.py>' % (bname,)
	pass
    
    locale.setlocale(locale.LC_CTYPE, '')
    try:
        encoding = locale.getlocale(locale.LC_CTYPE)[1]
    except:
        encoding = 'ascii'
        pass
    if len(sys.argv) != 2 and not (len(sys.argv) == 3 and sys.argv[1] == '-p'):
	usage()
	sys.exit()
	pass
    if len(sys.argv) == 2:
	fn = sys.argv[1]
    else:
	fn = sys.argv[2]
	pass
    fo = open(fn, 'r')
    fo = EncodedFile(fo, 'utf8', encoding)
    sys.stdout.write('# -*- coding: ' + encoding + ' -*-\n')
    if len(sys.argv) == 3 and sys.argv[1] == '-p':
	partial = True
    else:
	partial = False
	pass
    xml_to_template(fo, EncodedFile(sys.stdout, 'utf8', encoding), partial)
    pass
