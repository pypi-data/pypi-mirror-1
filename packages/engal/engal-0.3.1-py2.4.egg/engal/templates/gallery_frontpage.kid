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
<div id="header"><span /></div>

<table py:if="users" id="frontpage_table">
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
</table>

<!-- <div py:if="not tg.identity.anonymous">
<h3>Admin</h3>

</div> -->

</body>
</html>
