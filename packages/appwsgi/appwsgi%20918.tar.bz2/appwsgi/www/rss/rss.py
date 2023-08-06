# Copyright(c) gert.cuykens@gmail.com

def application(environ, response):
    xml  = '<?xml version="1.0" encoding="ISO-8859-1"?>'
    xml += '<rss version="2.0">'
    xml += ' <channel>'
    xml += '  <title>W3Schools Home Page</title>'
    xml += '  <link>http://www.w3schools.com</link>'
    xml += '  <description>Free web building tutorials</description>'
    xml += '  <item>'
    xml += '    <title>RSS Tutorial</title>'
    xml += '    <link>http://www.w3schools.com/rss</link>'
    xml += '    <description>New RSS tutorial on W3Schools</description>'
    xml += '  </item>'
    xml += ' </channel>'
    xml += '</rss>'
    response('200 OK',[('Content-type', 'text/xml'),('Content-Length', str(len(xml)))])
    return [xml]

