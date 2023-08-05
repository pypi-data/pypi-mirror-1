<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <style>
#addphotoset {  }
.invisible { display: none; }
    </style>

    <title>Photoset</title>
<script type="text/javascript">
    function toggleVisible(elem) {
        toggleElementClass("invisible", elem);
    }
</script>
</head>

<body class="engal">
  <div id="header">
    <h1>${photoset.title}</h1>
    <a href="#" target="#addphoto" REL="ibox?ibox_type=1&amp;height=300&amp;width=500" title="Add a photo" py:if="not tg.identity.anonymous">Add photo</a>
  </div>

<table id="photoset_table" align="center">
<tr>
<td width="250" id="photoset_details">

<?python
photo = photoset.getRandomPhoto()
?>
<div id="photoset_example" py:if="photo">
<A HREF="${tg.url('/photos/%s/%s/%d/%s' % (photoset.user.user_name, photoset.name, photo.id, photo.name))}"><IMG SRC="${tg.url('/image/%d/thumbnail/240x320' % (photo.id))}" BORDER="0" /></A>
</div>

<div class="photoset_info">
  <div><span class="photoset_name">${photoset.title}</span> <span>(created by <a href="${tg.url('/photos/%s' % (photoset.user.user_name))}">${photoset.user.user_name}</a>)</span></div>
  <div class="photoset_description">${photoset.description}</div>
  <div class="photoset_misc">This set contains ${photoset.photos.count()} photos.</div>
</div>

</td>
<td class="splitter"></td>
<td id="photoset_thumbs">

<?python
photos = photoset.photos[:]
?>

<h2>Photos in this set</h2>

<div class="thumbbox">

<div py:for="photo in photos">
<div class="thumb">
<A HREF="${tg.url('/photos/%s/%s/%d/%s' % (photoset.user.user_name, photoset.name, photo.id, photo.name))}"><IMG SRC="${tg.url('/image/%d/thumbnailbox/100' % (photo.id))}" BORDER="0" /></A>
</div>
</div>
</div>

<!-- <div class="next">next >>></div> -->

</td></tr></table>

<div id="addphoto" class="invisible"
py:content="photo_form(action=tg.url('/addPhoto'), value={'photoset_id':
photoset.id, 'return_path': '/photos/%s/%s' % (user.user_name, photoset.name)})">Add photo</div>

</body>
</html>
