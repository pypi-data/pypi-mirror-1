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
<img src="/static/images/spiderpy.gif" /> <br/>
<form action="/validateuser" method="post"> 
    <table>
        <th>Login info needed</th>
        <tr><td>Username:</td><td><textarea name="username" rows="1" cols="15"></textarea></td></tr>
        <tr><td>Password:</td><td><textarea name="password"  rows="1" cols="15" align = "right"></textarea></td></tr>
        <tr><td><input type="submit" name="submit" value="Login"/></td></tr>
    </table>
</form>
</body>
</html>
