from traceback import print_stack

global main_frame
main_frame = None

def set_main_frame(frame):
	global main_frame
	main_frame = frame

def get_main_frame():
	global main_frame
	return main_frame

def doc():
	global main_frame
	return main_frame.get_gdom_document()

def wnd():
	return doc().props.default_view

def JS(code):
	global main_frame
	ctx = main_frame.gjs_get_global_context()
	try:
		return ctx.eval(code)
	except:
		print "code", code
		print_stack()

global pygwt_moduleNames
pygwt_moduleNames = []

def pygwt_processMetas():
	import DOM
	global pygwt_moduleNames
	metas = doc().get_elements_by_tag_name("meta")
	for i in range(metas.props.length):
		meta = metas.item(i)
		name = DOM.getAttribute(meta, "name")
		if name == "pygwt:module":
			content = DOM.getAttribute(meta, "content")
			if content:
				pygwt_moduleNames.append(content)
	return pygwt_moduleNames
