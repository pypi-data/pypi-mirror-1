<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <style>
#addphotoset {  }
.invisible { display: none; }
    </style>

    <title>Engal tags</title>
<script type="text/javascript">
    function toggleVisible(elem) {
        toggleElementClass("invisible", elem);
    }
</script>
</head>

<body class="engal">

<div id="header">
  <h1>Tags</h1>
  <a href="#addtagaspect" REL="ibox?ibox_type=1&amp;height=300&amp;width=500" title="Add tag aspsect" py:if="not tg.identity.anonymous">Add Tag Aspect</a>
</div>

<h2>Tag aspects</h2>

<p>Tag aspects allow for tags to be placed into categories.  For example, a tag
may refer to a particular person, organisations, location, or event.  Or it may
describe the subject, the nature, or the style of the image.</p>

<p>The following tag aspects are set up in this gallery:</p>

<ul>
<li py:for="aspect in aspects"><p><a href="${tg.url('/tags/%s' % (aspect.short_name,))}"><span py:content="aspect.name">Location</span> (<span py:content="aspect.short_name">location</span>)</a></p><p py:content="aspect.description">This describes the location the image was taken or depicts.</p></li>
</ul>

<div id="addtagaspect" style="display: none;" py:content="tagaspect_form(action=tg.url('/tags/addTagAspect'), value={'return_path': tg.url('/tags')})">Add tag aspect</div>
<div id="addtag" style="display: none;" py:content="tag_form(action=tg.url('/tags/addTag'), value={'return_path': tg.url('/tags')})">Add tag aspect</div>

</body>
</html>
