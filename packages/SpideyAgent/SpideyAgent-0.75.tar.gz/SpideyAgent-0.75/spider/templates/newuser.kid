<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">

<head>
<link rel="stylesheet" type="text/css"
href="/static/css/site.css" />
<meta content="text/html; charset=UTF-8" http-equiv="content-type" />
<title>Welcome to Spiderpy</title>
</head>

<body >
<img src="/static/images/spiderpy.gif" />
<p ><span>Please fill in information about this new account</span></p>

<form action="/createuser" method="post"> 
	Username: <textarea name="username" rows="1" cols="30"></textarea> <br/>
	Password:<textarea name="password"  rows="1" cols="30"></textarea> <br/>
	Email Address: <textarea name="email"  rows="1" cols="30"></textarea> <br/>
	Interval:<textarea name="interval"  rows="1" cols="30"></textarea> <br/>
	<input type="submit" name="submit" value="Create"/> 
</form> 

</body>

</html>
