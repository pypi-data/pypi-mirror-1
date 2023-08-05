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
  <h1>Tags: <span py:replace="aspect.name" /></h1>
  <a href="#addtag" REL="ibox?ibox_type=1&amp;height=300&amp;width=500" title="Add sub-tag" py:if="not tg.identity.anonymous">Add Sub-tag</a>
</div>

<h2>About this tag</h2>

<p class="engal_tag_description" py:content="tag.description" />

<div py:if="tag.parentLocation and tag.parentLocation.depth > 0">
  <p><a href="${tg.url('/tags/%s/%s/' % (aspect.short_name, tag.parentLocation.short_name))}" py:content="tag.parentLocation.name">Africa</a> is the parent of this tag.</p>

<!--  <div py:content="tagparent_form(action=tg.url('/tags/reparentTag'),
  value=dict(tag_id = tag.id, parent_tag_id = tag.parentLocation.id),
  options=dict(parent_tag=dict(aspect=aspect)))" /> -->

  <div py:content="tagparent_form(action=tg.url('/tags/reparentTag'),
  value=dict(tag = tag.id, parent_tag = tag.parentLocation.id),
  options=dict(parent_tag=parent_options))" />
</div>
<div py:if="not (tag.parentLocation and tag.parentLocation.depth > 0)">
  <p>This tag has no parent.</p>

  <div py:content="tagparent_form(action=tg.url('/tags/reparentTag'),
  value=dict(tag = tag.id),
  options=dict(parent_tag=parent_options))" />
</div>


<div py:if="tag.childTags.count()">
<p>The following tags are children of this tag:</p>

<div py:def="display_tag(tag, min_depth = 1)">
    <p py:if="tag.depth >= min_depth"><a href="${tg.url('/tags/%s/%s/' % (aspect.short_name, tag.short_name))}"><span
    py:content="tag.name">Cape Town</span> (<span
    py:content="tag.short_name">capetown</span>)</a></p>
    <p py:if="tag.depth >= min_depth"
    py:content="tag.description" class="engal_tag_description">Pictures taken in Cape Town, South
    Africa</p>
    
    <ul py:if="tag.childTags.count()">
      <li py:for="child_tag in tag.childTags" py:content="display_tag(child_tag)">Stuff</li>
    </ul>
</div>

<div py:content="display_tag(tag, tag.depth + 1)" py:strip="True" />
</div>

<div id="addtag" style="display: none;" py:content="tag_form(action=tg.url('/tags/%s/addTag' % (aspect.short_name,)), value={'return_path': tg.url('/tags/%s' % (aspect.short_name,)), 'tag_aspect': aspect.id, 'parent_tag': tag.id})">Add tag aspect</div>

</body>
</html>
