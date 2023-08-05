<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">

<head>
<link rel="stylesheet" type="text/css"
href="/static/css/site.css" />
<meta content="text/html; charset=UTF-8" http-equiv="content-type" />
<title>Welcome to Spiderpy</title>
</head>

<body>

	
<form action="/search" method="post"> 
    <img src="/static/images/spiderpy.gif" /><br/>
    <textarea name="data" py:content="data" rows="1" cols="30">search text goes here</textarea>
    <input type="submit" name="submit" value="Search"/> 
</form> 
	

<table  border="0"  height="100%" width="100%" cellpadding="0" bgcolor="#a0c0ff" cellspacing="0">
  <tr height="100%" valign="bottom">
    <th align="left"><a  href="/login">Login</a></th>
    <th align="center"><a  href="/newuser">New User</a></th>
    <th align="right"><a  href="/admin">Admin</a></th>
    <TD></TD>
  </tr>
</table>

</body>

</html>
