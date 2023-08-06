def render(_init, nothing, request, options, xincludes, template, target_language=None):
	_out, _write = _init.initialize_stream()
	_attributes, repeat = _init.initialize_tal()
	_scope = {}
	_domain = None

	_write('<div>\n  Hello World!\n')
	_write('</div>')
	_write('\n')

	return _out.getvalue()
