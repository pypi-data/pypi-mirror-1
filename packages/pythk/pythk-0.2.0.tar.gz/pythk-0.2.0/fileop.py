def new_file(fn, content=''):
    fo = file(fn, 'w')
    fo.write(content)
    fo.close()
    pass

def append_line(fn, line=''):
    fo = file(fn, 'a')
    print >> fo, line
    fo.close()
    pass

def remove_lines(fn, ptn):
    import re
    reo = re.compile(ptn)
    
    fo = file(fn, 'r+')
    lines = fo.readlines()
    dlines = []
    for i, line in enumerate(lines):
	if reo.match(line):
	    dlines.append(i)
	    pass
	pass
    
    dcnt = 0
    for i in dlines:
	del lines[i - dcnt]
	dcnt = dcnt + 1
	pass
    
    fo.seek(0)
    fo.truncate()
    fo.writelines(lines)
    pass

def empty_file(fn):
    fo = file(fn, 'w')
    fo.close()
    pass

def copy_file(fn1, fn2):
    fo1 = file(fn1, 'r')
    fo2 = file(fn2, 'w')
    content = fo1.read()
    fo2.write(content)
    fo2.close()
    fo1.close()
    pass

def make_backup(fn):
    fnbk = fn + '~'
    copy_file(fn, fnbk)
    pass

def file_has_line(fn, ptn):
    import re
    
    fo = file(fn, 'r')
    reo = re.compile(ptn)
    for line in fo:
	if reo.match(line):
	    return True
	pass
    return False
