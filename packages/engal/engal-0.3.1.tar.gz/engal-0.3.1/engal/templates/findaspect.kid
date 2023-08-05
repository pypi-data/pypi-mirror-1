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
  <h1>Find by <span py:replace="aspect.name" /></h1>
</div>

<p py:content="aspect.description" />

<p>The following tags are in this aspect:</p>

<div py:def="display_tag(tag, min_depth = 1)">
    <p py:if="tag.depth >= min_depth"><a href="${tg.url('/find/%s/%s/' % (aspect.short_name, tag.short_name))}"><span
    py:content="tag.name">Cape Town</span> (<span
    py:content="tag.short_name">capetown</span>)</a> - <span py:content="tag.photos.count()">2</span> photos</p>
    <p py:if="tag.depth >= min_depth"
    py:content="tag.description" class="engal_tag_description">Pictures taken in Cape Town, South
    Africa</p>
    
    <ul py:if="tag.childTags">
      <li py:for="child_tag in tag.childTags" py:content="display_tag(child_tag)">Stuff</li>
    </ul>
</div>

<div py:content="display_tag(aspect.rootTag)" py:strip="True" />

</body>
</html>
