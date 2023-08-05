<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <style>
#addphotoset {  }
.invisible { display: none; }
    </style>

    <title>Welcome to TurboGears</title>
<script type="text/javascript">
    function toggleVisible(elem) {
        toggleElementClass("invisible", elem);
    }
</script>
</head>

<body class="engal">

<div id="header">
  <h1>Sets</h1>
  <a href="#addphotoset" REL="ibox?ibox_type=1&amp;height=300&amp;width=500" title="Add photoset" py:if="not tg.identity.anonymous">Add photoset</a>
</div>

<table id="userpage_table" py:if="photosets" align="center">
<tr py:for="photoset in photosets">
<td class="userpage_details">
<?python
photo = photoset.getRandomPhoto()
?>
<div py:if="photo">
<a href="${tg.url('/gallery/%s/sets/%s' % (user.user_name, photoset.name))}"><img src="${tg.url('/image/%d/thumbnailbox/150' % (photo.id))}" /></a>
</div>
<p py:if="not photo">&nbsp;</p>
</td>
<td class="splitter">
</td>
<td>

<div class="photoset_info">
  <div>
    <span class="photoset_name"><a href="${tg.url('/gallery/%s/sets/%s' % (user.user_name, photoset.name))}">${photoset.title}</a></span>
  </div>
</div>

<div class="userpage_thumbs">
<div py:for="photo in photoset.photos[:8]">
<div class="thumb">
<A HREF="${tg.url('/gallery/%s/images/%s/set-%s' % (user.user_name, photo.name, photoset.name))}"><IMG SRC="${tg.url('/image/%d/thumbnailbox/70' % (photo.id))}" BORDER="0" /></A>
</div>
</div>
</div>

<div class="photoset_info">
  <div class="photoset_description">${photoset.description}</div>
  <div class="photoset_misc">This set contains ${photoset.photos.count()} photos.</div>
</div>

</td>
</tr>
</table>

<div id="addphotoset" style="display: none;" py:content="photoset_form(action=tg.url('/addPhotoSet'), value={'return_path': tg.url('/gallery/%s' % (user.user_name))})">Add photoset</div>

</body>
</html>
