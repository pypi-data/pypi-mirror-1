<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Welcome to TurboGears</title>
</head>

<body>
    <p>Your TurboGears server is running as of <span py:replace="now">now</span>.</p>
    
    <h2>Quick! Dive right in!</h2>
    
    <p>Here's what you'll likely want to do:</p>

    <ol>
        <li>Edit your project's model.py to create SQLObjects representing the data you're working with</li>
        <li>Edit your dev.cfg file to point to the database you'll be using</li>
        <li>Run "<code>tg-admin sql create</code>" to create the tables in the database</li>
        <li>Edit controllers.py to add the functionality to your webapp</li>
        <li>Change the master.kid template to have the headers and footers for your application.</li>
        <li>Change this template or create a new one to display your data</li>
        <li>Repeat steps 4-6 until done.</li>
        <li><b>Profit!</b></li>
    </ol>
    
    <p>If you haven't already, you might check out some of the <a href="http://www.turbogears.org/docs/" target="_blank">documentation</a>.</p>
    
    <p>Thanks for using TurboGears! See you on the <a href="http://groups.google.com/group/turbogears" target="_blank">mailing list</a> and the "turbogears" channel on irc.freenode.org!</p>
    
</body>
</html>