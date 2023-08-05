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

Results for <textarea name="data" py:content="data" rows="1" cols="20"/> 
<a href="${tg.url(['/validateuser',username])}">Back to my page</a>
<hr/>
<li py:for="x in sites"><a href= " ${x}" >${x}</a><br/>${descriptions[x]}</li>

<hr/>
<span py:for="y in range(numberofpages)"> <a href="${tg.url(['/search',data,username,str(y)])}">${y}</a> </span>

</body>
</html>
