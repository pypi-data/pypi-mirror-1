"""Various templates used to generate files
"""

DELIVERANCE_INI = """\
[DEFAULT]
debug = %(debug)s
#error_email = 

[server:main]
use = egg:Paste#http
host = %(host)s
port = %(port)s

[app:main]
use = egg:Deliverance#proxy
wrap_href = %(proxy)s
mount /.deliverance = %(location)s
theme_uri = %(theme)s
rule_uri = %(rules)s
transparent = %(transparent)s
relocate_content = %(rewrite)s
serializer = %(serializer)s

[exe]
command = serve
pid_file = %(directory)s/var/run/%(name)s.pid
log_file = %(directory)s/var/log/%(name)s.log
daemon = true
#user = username
#group = groupname
"""

DEFAULT_RULES = """\
<?xml version="1.0" encoding="UTF-8"?>
<rules xmlns:xi="http://www.w3.org/2001/XInclude" xmlns="http://www.plone.org/deliverance" >
  <xi:include href="standardrules.xml" />

  <copy theme="//div[@id='content']" content="//*[@id='portal-columns']" />
</rules>
"""

STANDARD_RULES = """\
<?xml version="1.0" encoding="UTF-8"?>
<rules xmlns:xi="http://www.w3.org/2001/XInclude" xmlns="http://www.plone.org/deliverance">
  <prepend theme="//head" content="//head/link" nocontent="ignore" /> 
  <prepend theme="//head" content="//head/style" nocontent="ignore" /> 
  <append theme="//head" content="//head/script" nocontent="ignore" />    
  <append theme="//head" content="//head/meta" nocontent="ignore" />
  <append-or-replace theme="//head" content="//head/title"
   nocontent="ignore" />
</rules>
"""
DEFAULT_THEME = """\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-15">
<title>The Theme</title>
</head>

<body>
<h1>A theme</h1>

<div id="content">
</div>


<hr>
<address></address>
<!-- hhmts start -->Last modified: Fri Mar 16 09:33:37 CDT 2007 <!-- hhmts end -->
</body> </html>
"""
