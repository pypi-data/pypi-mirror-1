<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <style>
#addphotoset {  }
.invisible { display: none; }
    </style>

    <title>Photo</title>
<script type="text/javascript">
    function toggleVisible(elem) {
        toggleElementClass("invisible", elem);
    }
</script>
</head>

<body class="engal">
  <div id="header">
    <h1> ${photo.name} </h1>
    <a href="#" target="#editphoto" REL="ibox?ibox_type=1&amp;height=300&amp;width=500" title="Edit photo" py:if="not tg.identity.anonymous">Edit photo</a>
  </div>

<table id="photo_table" align="center">
<tr>
<td width="250" id="photo_details">

<div id="photo_photo">
<IMG SRC="${tg.url('/image/%d/thumbnail/640x480' % (photo.id))}" BORDER="0" />
</div>

<div class="photo_info">
  <div><span class="photo_name">${photo.name}</span> <span>(by <a href="${tg.url('/gallery/%s' % (photo.owner.user_name))}">${photo.owner.user_name}</a>)</span></div>
  <div class="photo_description">${photo.description}</div>
</div>

<dl>
  <div py:for="aspect, tags in photo.taginfo" py:strip="True">
    <dt py:content="aspect.name">Location</dt>
    <dd py:for="tag in tags" py:content="tag.name">Cape Town</dd>
  </div>
</dl>

<div py:content="tag_form(action=tg.url('/gallery/%s/saveTags' % (user.user_name,)),
value=dict(photo_id=photo.id, return_url=return_url))">Edit tags</div>

</td>
<td class="splitter"></td>
<td id="photo_other">

<div class="engal_tags">
<div py:for="aspect, tags in taginfo.items()">
  <div py:for="tag in tags" py:content="tag.name" class="engal_tag engal_tagaspect_${aspect.short_name}">Cape Town</div>
</div>
</div>

<div id="photo_primary_photoset">
<div class="photoset_info">
  <div>Part of the <a href="${tg.url('/gallery/%s/sets/%s' % (photoset.user.user_name, photoset.name))}"><span class="photoset_name">${photoset.title}</span></a> set</div>
  <div class="photoset_description">${photoset.description}</div>
</div>
<?python
photos = [p for p in photoset.photos[:] if p.id != photo.id]
?>


<div class="thumbbox" py:if="photoset.photos.count() > 1">
<div class="others_in_the_set">Other photos in this set...</div>
<div py:for="thumb_photo in photos[:24]">
<!-- ${ibox.display('/image/%d/thumbnail/640' % (photo.id), thumb_url='/image/%d/thumbnailbox/100' % (photo.id))} -->
<div class="thumb">
<A HREF="${tg.url('/gallery/%s/images/%s/set-%s' % (user.user_name, thumb_photo.name, photoset.name))}"><IMG SRC="${tg.url('/image/%d/thumbnailbox/40' % (thumb_photo.id))}" BORDER="0" /></A>
</div>
</div>
</div>
<div class="photoset_info">
  <p class="photoset_misc">This set contains ${photoset.photos.count()} photos.</p>
</div>
</div>

</td></tr></table>

<div id="editphoto" class="invisible"
py:content="editphoto_form(action=tg.url('/editPhoto'), value={'photo_id': photo.id, 'return_path': tg.url('/gallery/%s/images' % (user.user_name)), 'name': photo.name, 'description': photo.description})">Edit photo</div>

</body>
</html>
