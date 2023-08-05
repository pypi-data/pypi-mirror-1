<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <style>
#addphotoset {  }
.invisible { display: none; }
    </style>

    <title>Engal tags: <span py:replace="aspect.name" /></title>
<script type="text/javascript">
    function toggleVisible(elem) {
        toggleElementClass("invisible", elem);
    }
</script>
</head>

<body class="engal">

<div id="header">
  <h1>Find by <span py:content="aspect.name">Location</span>: <span py:content="tag.name">Africa</span></h1>
</div>

<table id="photoset_table" align="center">
<tr>
<td width="250" id="photoset_details">

<?python
#photo = tag.getRandomPhoto()
photo = None
?>
<div id="photoset_example" py:if="photo">
<a href="${tg.url('/gallery/%s/images/%s/set-%s' % (photoset.user.user_name, photo.name, photoset.name))}"><img src="${tg.url('/image/%d/thumbnail/240x320' % (photo.id))}" border="0" /></a>
</div>

<div class="photoset_info">
  <div><span class="photoset_name">${tag.name}</span></div>
  <div class="photoset_description">${tag.description}</div>
  <div class="photoset_misc">This tag contains ${photos.count()} photos.</div>
</div>

<div py:if="tag.childTags.count()">
<p>The following tags are children of this tag:</p>

<div py:def="display_tag(tag, min_depth = 1)">
    <p py:if="tag.depth >= min_depth"><a href="${tg.url('/find/%s/%s/' % (aspect.short_name, tag.short_name))}"><span
    py:content="tag.name">Cape Town</span> (<span
    py:content="tag.short_name">capetown</span>)</a></p>
    <p py:if="tag.depth >= min_depth"
    py:content="tag.description" class="engal_tag_description">Pictures taken in Cape Town, South
    Africa</p>
    
    <ul py:if="tag.childTags">
      <li py:for="child_tag in tag.childTags" py:content="display_tag(child_tag)">Stuff</li>
    </ul>
</div>

<div py:content="display_tag(tag, tag.depth + 1)" py:strip="True" />
</div>


</td>
<td class="splitter"></td>
<td id="photoset_thumbs">

<h2>Photos with this tag</h2>

<div class="thumbbox">

<div py:for="photo in photos">
<div class="thumb">
<A HREF="${tg.url('/gallery/%s/images/%s' % (photo.owner.user_name, photo.name))}"><IMG SRC="${tg.url('/image/%d/thumbnailbox/100' % (photo.id))}" BORDER="0" /></A>
</div>
</div>
</div>

</td></tr></table>


</body>
</html>
