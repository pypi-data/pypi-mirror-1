<html>
<body>
%if h.has_permission('add_users'):
<div>Add user</div>
%endif
%if c.current_user:
<div>Post</div>
%endif
</body>
</html>