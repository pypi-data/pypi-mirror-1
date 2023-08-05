<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">

<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title py:replace="''">Your title goes here</title>
    <meta py:replace="item[:]"/>
    <style type="text/css">
        @import '${tg.url('/static/css/engal.css')}';
    </style>
</head>

<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()">

  <div py:match="item.tag=='{http://www.w3.org/1999/xhtml}div' and item.get(u'id')=='header'" py:attrs="item.items()" id="header">
    <?python
    h1 = [e for e in item[:] if e.tag == "{http://www.w3.org/1999/xhtml}h1"]
    if h1:
        h1 = h1[0]
        item = [e for e in item[:] if e.tag != "{http://www.w3.org/1999/xhtml}h1"]
    else:
        h1 = ''
    ?>
    <div id="nav">
      <div py:replace="item[:]" />
      <span py:if="tg.config('identity.on',False) and not 'logging_in' in locals()"
         id="pageLogin">
        <!-- <a href="${tg.url('/find')}">Find</a> -->
        <span py:if="tg.identity.anonymous">
          <a href="${tg.url('/login')}">Login</a>
        </span>
        <span py:if="not tg.identity.anonymous">
          <a href="${tg.url('/tags')}">Manage tags</a>
          <a href="${tg.url('/logout')}">Logout</a>
        </span>
      </span>
      <div py:if="not tg.identity.anonymous" class="welcome">Welcome ${tg.identity.user.display_name}.</div>
    </div>
    <h1 py:replace="h1">Favourites</h1>
  </div>


  <div py:if="tg_flash" class="flash" py:content="tg_flash"></div>

  <?python
  header = [i for i in item[:] if i.get(u'id') == 'header']
  if header:
      header = header[0]
  else:
      header = ''
  item = [i for i in item[:] if not (i.get(u'id') == 'header')]
  ?>
  <div py:replace="header"/>
  <div id="engal_contents">
    <div py:replace="item[:]"/>
  </div>

  <p align="center"><img src="${tg.url('/static/images/tg_under_the_hood.png')}" alt="TurboGears under the hood"/></p>
</body>

</html>
