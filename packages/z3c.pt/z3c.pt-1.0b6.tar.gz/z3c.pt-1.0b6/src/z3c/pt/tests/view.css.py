def render(_init, template, xincludes, request, context, nothing, options, view, target_language=None):
	_out, _write = _init.initialize_stream()
	_attributes, repeat = _init.initialize_tal()
	_scope = {}
	_domain = None

	# _path(options, request, True, 'color')
	_write('#region {\n    background: ')
	_tmp1 = _path(options, request, True, 'color')
	_tmp = _tmp1
	if _tmp is not None:
		if not isinstance(_tmp, (str, unicode)):
			_tmp = str(_tmp)
		_write(_tmp)
	_validate(_tmp)
	_write(';\n}')

	return _out.getvalue()
