<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <style>
#addphotoset {  }
.invisible { display: none; }
    </style>

    <title>Welcome to Engal</title>
<script type="text/javascript">
    function toggleVisible(elem) {
        toggleElementClass("invisible", elem);
    }
</script>
</head>

<body class="engal">
<div id="header"><h1>Welcome</h1></div>

<table id="frontpage_table">

<tr>
<td width="50%">

<table id="frontpage_userlist_table">
<thead>
<caption>Contributors to the gallery</caption>
</thead>
<tbody>
<tr py:for="user in users">

<!-- <div style="float: left" py:for="photoset in photosets"> -->
<td class="frontpage_thumbnail">
<?python
photo = user.getRandomPhoto()
?>
<div py:if="photo">
<a href="${tg.url('/gallery/%s' % (user.user_name))}"><img src="${tg.url('/image/%d/thumbnailbox/150' % (photo.id))}" /></a>
</div>
<p py:if="not photo">&nbsp;</p>
</td>
<td class="splitter">
</td>
<td class="frontpage_details">
<div class="frontage_user_details">
<a href="${tg.url('/gallery/%s' % (user.user_name))}">${user.display_name}</a>
<div>This user has ${user.photosets.count()} sets</div>
<div>This user has ${user.photos.count()} photos</div>
</div>

</td>
</tr>
</tbody>
</table>

</td>
<td>

<div id="frontpage_find" py:if="aspects.count()">
<h2>Find images by...</h2>
<div py:for="aspect in aspects">
  <p py:content="'%s:' % (aspect.name,)" class="engal_tag engal_tagaspect_${aspect.short_name}">Location:</p>
  <p py:if="aspect.tags.count()" class="engal_tag_list"><span py:for="tag in aspect.tags[:5]" py:content="tag.name + ', '" /> ... </p>
</div>
</div>

</td>
</tr>
</table>

<!-- <div py:if="not tg.identity.anonymous">
<h3>Admin</h3>

</div> -->

</body>
</html>
