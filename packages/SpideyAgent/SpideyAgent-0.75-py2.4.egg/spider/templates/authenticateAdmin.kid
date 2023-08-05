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
<div>
<p><span><h2>Admin login</h2></span></p><hr/>
<table border="1" >
    <tr valign="top">
        <th>Account Information</th>
    </tr>
    <tr valign="top">
        <td width="100%" >
            <form action="/adminAuth" method="post"> 
                Password:<textarea name="password" rows="1" cols="30"></textarea><br/>
                <input type="submit" name="submit" value="login"/> 
            </form>
        </td>
    </tr>
</table>
</div>
</body>
</html>
