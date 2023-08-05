<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#">
    <head>
        <title py:content="title">Title goes here</title>
    </head>

    <body>
	    <h1 py:content="message">Message goes here</h1>
	    <p>
		    Here is some cherrypy.data!<br />
		    cherrypy.request.remoteAddr = ${cherrypy.request.remoteAddr}
	    </p>
    </body>
</html>

