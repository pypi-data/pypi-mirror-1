<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <style>
#addphotoset {  }
.invisible { display: none; }
    </style>

    <title>There has been an error in this form</title>
<script type="text/javascript">
    function toggleVisible(elem) {
        toggleElementClass("invisible", elem);
    }
</script>
</head>

<body class="engal">
  <div id="header">
    <h1> Form error </h1>
  </div>

<div py:content="form(action=form_action)">Edit tags</div>

</body>
</html>
