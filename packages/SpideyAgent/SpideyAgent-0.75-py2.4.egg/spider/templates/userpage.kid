<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<head>
<link rel="stylesheet" type="text/css"
href="/static/css/site.css" />
<meta content="text/html; charset=UTF-8" http-equiv="content-type" />
<title > Welcome to Spiderpy ${username}</title>
</head>
<body >
<div >
<img src="/static/images/spiderpy.gif" />
<a href="/">Home</a>
<table border="1" >
	<tr>
	<th>Spider Controls</th>
	<th>Search and Statistics</th>
	<th>Root Sites</th>
	</tr>
	<tr valign="top">
		<td>
			<form action="/add" method="post"> 
			    <input type="hidden" name="username" value="${username}"/> 
				<input type="submit" name="submit" value="Add New Site to be spidered"/> 
			</form> 
			<form action="/start" method="post"> 
			    <input type="hidden" name="username" value="${username}"/> 
				<input type="submit" name="submit" value="Start Spider"/> 
			</form> 
			<form action="/stop" method="post"> 
			    <input type="hidden" name="username" value="${username}"/> 
				<input type="submit" name="submit" value="Stop Spider"/> 
			</form>
			<form action="/clearQ" method="post"> 
			    <input type="hidden" name="username" value="${username}"/> 
				<input type="submit" name="submit" value="Clear que"/> 
			</form>
			<form action="/setInterval" method="post"> 
			    <input type="hidden" name="username" value="${username}"/> 
			    <input type="submit" name="submit" value="Set update interval for all sites"/> 
			    <textarea name="time" py:content="time" rows="1" cols="30"></textarea>
			</form>
		</td>
		<td width="100%" >Total words found ${numberofwords}<br/>Sites spidered ${numberofsites}<br/> Sites in que ${numberinque}<br/> 
		    <p> 
		        <form action="/search" method="post"> 
                	<input type="submit" name="submit" value="Search"/> 
                	<input type="hidden" name="username" value="${username}"/> 
                	<textarea name="data" rows="1" cols="30"></textarea>
                </form>
		    </p>
		</td>
		<td width="100%">
			<form py:for="x in root_sites" action="/deleteSite" method="post"> ${x}<input type="hidden" name="user" value="${username}"/><input type="hidden" name="address" value="${x}"/>
				<input type="submit" name="submit" value="Delete"/> 
			</form>
		</td>
	</tr>
</table>
</div>
</body>
</html>
