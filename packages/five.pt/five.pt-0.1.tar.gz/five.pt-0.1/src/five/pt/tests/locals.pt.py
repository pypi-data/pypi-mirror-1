def render(_init, container, context, xincludes, views, modules, request, here, template, nothing, root, options, view, target_language=None):
	_out, _write = _init.initialize_stream()
	_attributes, repeat = _init.initialize_tal()
	_scope = {}
	_domain = None

	# join('view:', value("_path(view, request, True, 'available')"))
	_write('<div>\n    ')
	_content = '%s%s' % ('view:',_path(view, request, True, 'available'))
	# _content
	_tmp1 = _content
	_tmp = _tmp1
	if _tmp is not None:
		if not isinstance(_tmp, (str, unicode)):
			_tmp = str(_tmp)
		if '&' in _tmp:
			_tmp = _tmp.replace('&', '&amp;')
		if '<' in _tmp:
			_tmp = _tmp.replace('<', '&lt;')
		if '>' in _tmp:
			_tmp = _tmp.replace('>', '&gt;')
		if '"' in _tmp:
			_tmp = _tmp.replace('"', '&quot;')
		_write(_tmp)
	_validate(_tmp)
	# 'here==context:'+str(here==context)
	_write('\n    ')
	_content = 'here==context:'+str(here==context)
	# _content
	_tmp1 = _content
	_tmp = _tmp1
	if _tmp is not None:
		if not isinstance(_tmp, (str, unicode)):
			_tmp = str(_tmp)
		if '&' in _tmp:
			_tmp = _tmp.replace('&', '&amp;')
		if '<' in _tmp:
			_tmp = _tmp.replace('<', '&lt;')
		if '>' in _tmp:
			_tmp = _tmp.replace('>', '&gt;')
		if '"' in _tmp:
			_tmp = _tmp.replace('"', '&quot;')
		_write(_tmp)
	_validate(_tmp)
	# 'here==container:'+str(here==container)
	_write('\n    ')
	_content = 'here==container:'+str(here==container)
	# _content
	_tmp1 = _content
	_tmp = _tmp1
	if _tmp is not None:
		if not isinstance(_tmp, (str, unicode)):
			_tmp = str(_tmp)
		if '&' in _tmp:
			_tmp = _tmp.replace('&', '&amp;')
		if '<' in _tmp:
			_tmp = _tmp.replace('<', '&lt;')
		if '>' in _tmp:
			_tmp = _tmp.replace('>', '&gt;')
		if '"' in _tmp:
			_tmp = _tmp.replace('"', '&quot;')
		_write(_tmp)
	_validate(_tmp)
	# join('root:', value("_path(root, request, True, 'getPhysicalPath')"))
	_write('\n    ')
	_content = '%s%s' % ('root:',_path(root, request, True, 'getPhysicalPath'))
	# _content
	_tmp1 = _content
	_tmp = _tmp1
	if _tmp is not None:
		if not isinstance(_tmp, (str, unicode)):
			_tmp = str(_tmp)
		if '&' in _tmp:
			_tmp = _tmp.replace('&', '&amp;')
		if '<' in _tmp:
			_tmp = _tmp.replace('<', '&lt;')
		if '>' in _tmp:
			_tmp = _tmp.replace('>', '&gt;')
		if '"' in _tmp:
			_tmp = _tmp.replace('"', '&quot;')
		_write(_tmp)
	_validate(_tmp)
	# join('nothing:', value('_path(None, request, True, )'))
	_write('\n    ')
	_content = '%s%s' % ('nothing:',_path(None, request, True, ))
	# _content
	_tmp1 = _content
	_tmp = _tmp1
	if _tmp is not None:
		if not isinstance(_tmp, (str, unicode)):
			_tmp = str(_tmp)
		if '&' in _tmp:
			_tmp = _tmp.replace('&', '&amp;')
		if '<' in _tmp:
			_tmp = _tmp.replace('<', '&lt;')
		if '>' in _tmp:
			_tmp = _tmp.replace('>', '&gt;')
		if '"' in _tmp:
			_tmp = _tmp.replace('"', '&quot;')
		_write(_tmp)
	_validate(_tmp)
	# modules['cgi']
	_write('\n    ')
	cgi = modules['cgi']
	# cgi.escape(view.tagsoup())
	_write('<div>\n        modules:')
	_content = cgi.escape(view.tagsoup())
	# _content
	_tmp2 = _content
	_tmp = _tmp2
	if _tmp is not None:
		if not isinstance(_tmp, (str, unicode)):
			_tmp = str(_tmp)
		if '&' in _tmp:
			_tmp = _tmp.replace('&', '&amp;')
		if '<' in _tmp:
			_tmp = _tmp.replace('<', '&lt;')
		if '>' in _tmp:
			_tmp = _tmp.replace('>', '&gt;')
		if '"' in _tmp:
			_tmp = _tmp.replace('"', '&quot;')
		_write(_tmp)
	_validate(_tmp)
	_write('\n    ')
	_write('</div>')
	_write('\n')
	del cgi
	_write('</div>')
	_write('\n')

	return _out.getvalue()
