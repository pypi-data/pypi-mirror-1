import sys

about_content = """
<html>
 <head>
  <title>Orbited 0.1.3</title>
 </head>
 <body>
  <h1>Orbited 0.1.3</h1>
  Python %s
 </body>
</html>""" % sys.version

about_header = """HTTP/1.0 200 OK
Connection: close
Content-Type: text/html
Content-Length: %s

""" % len(about_content)

about = about_header + about_content
