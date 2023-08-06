def render(_init, container, context, xincludes, views, modules, request, here, template, nothing, root, options, view, target_language=None):
	_out, _write = _init.initialize_stream()
	_attributes, repeat = _init.initialize_tal()
	_scope = {}
	_domain = None

	# _path(options, request, True, )
	_write('<div>\n    ')
	_tmp2 = _path(options, request, True, )
	_tmp2 = repeat.insert('key', _tmp2)
	try:
		key = None
		key = _tmp2.next()
		while True:
			# _path(key, request, True, )
			_write('<div>\n        ')
			_content = _path(key, request, True, )
			# _content
			_tmp3 = _content
			_tmp = _tmp3
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
			# options[key]
			_write(' : ')
			_content = options[key]
			# _content
			_tmp3 = _content
			_tmp = _tmp3
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
			key = _tmp2.next()
			_write('\n')
	except StopIteration:
		pass
	del key
	_write('\n')
	_write('</div>')
	_write('\n')

	return _out.getvalue()
