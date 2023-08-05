<%args>
title, message
</%args>

<html>
    <head>
	    <title><% title %></title>
    </head>

    <body>
	    <h1><% message %></h1>
		<p>Here is something from CherryPy:</p>
		<p>cherrypy.request.remoteAddr:
			<% cherrypy.request.remoteAddr %>
		</p>
    </body>
</html>

