def render(_init, _out=None, _write=None, _scope=None, xincludes=None, target_language=None, ):
	_attributes, repeat = _init.initialize_tal()
	_domain = None
	_write('<div>\n  <span>Hello, world!')
	_write('</span>')
	_write('\n')
	_write('</div>')
	_write('\n')

