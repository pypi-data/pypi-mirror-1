from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
_magic_number = 2
_modified_time = 1184705476.432349
_template_filename='/Users/danjac/petprojects/tesla-pylons-elixir/tests/output/AuthProjectName/authprojectname/templates/index.mako'
_template_uri='/index.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = []


def render_body(context,**pageargs):
    context.caller_stack.push_frame()
    try:
        __M_locals = dict(pageargs=pageargs)
        h = context.get('h', UNDEFINED)
        c = context.get('c', UNDEFINED)
        # SOURCE LINE 1
        context.write(u'<html>\n<body>\n')
        # SOURCE LINE 3
        if h.has_permission('add_users'):
            # SOURCE LINE 4
            context.write(u'<div>Add user</div>\n')
        # SOURCE LINE 6
        if c.current_user:
            # SOURCE LINE 7
            context.write(u'<div>Post</div>\n')
        # SOURCE LINE 9
        context.write(u'</body>\n</html>')
        return ''
    finally:
        context.caller_stack.pop_frame()


