def render(_init, template, xincludes, request, context, nothing, options, view, target_language=None):
	_out, _write = _init.initialize_stream()
	_attributes, repeat = _init.initialize_tal()
	_scope = {}
	_domain = None

	# _path(view, request, True, )
	_write('<div>\n  ')
	_content = _path(view, request, True, )
	# not (_content is None)
	_tmp1 = not (_content is None)
	if _tmp1:
		_write('<span>')
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
	if _tmp1:
		_write('</span>')
	# _path(context, request, True, )
	_write('\n  ')
	_content = _path(context, request, True, )
	# not (_content is None)
	_tmp1 = not (_content is None)
	if _tmp1:
		_write('<span>')
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
	if _tmp1:
		_write('</span>')
	# _path(request, request, True, )
	_write('\n  ')
	_content = _path(request, request, True, )
	# not (_content is None)
	_tmp1 = not (_content is None)
	if _tmp1:
		_write('<span>')
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
	if _tmp1:
		_write('</span>')
	# _path(options, request, True, 'test')
	_write('\n  ')
	_content = _path(options, request, True, 'test')
	# not (_content is None)
	_tmp1 = not (_content is None)
	if _tmp1:
		_write('<span>')
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
	if _tmp1:
		_write('</span>')
	_write('\n')
	_write('</div>')
	_write('\n')

	return _out.getvalue()
