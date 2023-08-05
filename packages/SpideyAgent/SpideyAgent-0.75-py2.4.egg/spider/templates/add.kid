<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<head>
<meta content="text/html; charset=UTF-8" http-equiv="content-type" />
<title>Welcome to Spiderpy</title>
</head>
<body>
<div >
<p ><span>Add a site </span></p><hr/>
<form action="insertNewSite" method="post"> 
    <input type="hidden" name="username" value="${username}"/> 
    <table>
        <tr><td>Address</td> <td align="right"><textarea name="address"  rows="1" cols="30"></textarea></td> </tr>
        <tr><td><input type="submit" name="submit" value="Add"/></td></tr>
    </table>
</form> 
</div>
</body>
</html>
