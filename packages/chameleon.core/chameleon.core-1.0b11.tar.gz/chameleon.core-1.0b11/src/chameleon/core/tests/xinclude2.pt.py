def bind():
	from chameleon.core import generation as _init
	def render(_domain = None, xincludes = None, econtext = None, _out = None, _write = None, target_language = None):
		_attributes, repeat = _init.initialize_tal()
		_domain = None
		_write('<div>\n  <span>Hello, world!')
		_write('</span>')
		_write('\n')
		_write('</div>')
		_write('\n')
		
		return 
	return render
