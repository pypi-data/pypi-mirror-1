<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>First user creation</title>
</head>

<body class="engal">
  <div id="header">
    <h1> First user creation </h1>
  </div>

<table id="firstuser_table" align="center">
<tr><td>

<div id="adduser" py:content="adduser_form(action=tg.url('/firstuser_create'))">Add User</div>

</td></tr></table>

</body>
</html>
