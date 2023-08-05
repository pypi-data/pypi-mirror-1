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
        <p>When properly configured, as in this demo, 
           <a href="exception">Myghty exceptions</a>
           propogate down to CherryPy and can be handled as any other
           exception.
        </p>
    </body>
</html>

