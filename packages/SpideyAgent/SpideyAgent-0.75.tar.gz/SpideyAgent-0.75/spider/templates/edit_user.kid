<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">

<head>
<meta content="text/html; charset=UTF-8" http-equiv="content-type" />
<title>Welcome to Spiderpy</title>
</head>

<body>

<div >

<p><span></span></p>

<p ><span><h2>Edit Account</h2></span></p> <hr/>

<table border="1" >
    <tr valign="top">
        <th>Account Information</th>
    </tr>
    <tr valign="top">
        <td width="100%" >
            <form action="save_changes" method="post"> 
                Username: <textarea name="username" rows="1" cols="30">${name}</textarea> <br/>
                Password:<textarea name="password"  rows="1" cols="30">${password}</textarea> <br/>
                Email Address: <textarea name="email"  rows="1" cols="30">${email}</textarea> <br/>
                Interval:<textarea name="interval"  rows="1" cols="30">${interval}</textarea> <br/>
                <input type="submit" name="submit" value="Save"/> 
            </form>
        </td>
    </tr>
</table> 

</div>

</body>

</html>
