def render(_init, xincludes, target_language=None):
	_out, _write = _init.initialize_stream()
	_attributes, repeat = _init.initialize_tal()
	econtext = _init.initialize_scope()
	_domain = None

	# 'xinclude2.pt'
	_write('<div>\n  ')
	_include = 'xinclude2.pt'
	# %(xincludes)s.get(%(include)s, 'xml').render_xinclude(_domain=_domain, xincludes=xincludes, econtext=econtext, _out=_out, _write=_write, target_language=target_language)
	_tmp1 = xincludes.get(_include, 'xml').render_xinclude(_domain=_domain, xincludes=xincludes, econtext=econtext, _out=_out, _write=_write, target_language=target_language)
	_tmp = _tmp1
	if _tmp is not None:
		if not isinstance(_tmp, (str, unicode)):
			_tmp = str(_tmp)
		_write(_tmp)
	_write('\n')
	_write('</div>')
	_write('\n')

	return _out.getvalue()
