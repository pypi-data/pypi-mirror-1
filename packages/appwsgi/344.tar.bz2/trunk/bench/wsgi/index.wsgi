def application(environ, response):
    output = 'Hello, World!'
    response('200 OK',[('Content-type', 'text/plain'),('Content-Length', str(len(output)))])
    return [output] 
 
