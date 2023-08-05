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

<div >

<p ><span><h2>Admin</h2></span></p> <hr/>

<table border="1" >
    <tr valign="top">
        <th>Users</th>
    </tr>
    <tr valign="top">
        <td width="100%" >
            <form py:for="x in users" action="/edit_user" method="post"> 
                ${x} 
                <input type="hidden" name="username" value="${x}"/>
                <input type="submit" name="submit" value="Edit account"/> 
            </form>
        </td>
    </tr>
</table> 

</div>

</body>

</html>
