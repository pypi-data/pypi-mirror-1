<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <style>
#addphotoset {  }
.invisible { display: none; }
    </style>

    <title>Find images...</title>
<script type="text/javascript">
    function toggleVisible(elem) {
        toggleElementClass("invisible", elem);
    }
</script>
</head>

<body class="engal">

<div id="header">
  <h1>Find</h1>
  <a href="#addtag" REL="ibox?ibox_type=1&amp;height=300&amp;width=500" title="Add tag" py:if="not tg.identity.anonymous">Add Tag</a>
</div>

<div>
<p style="font-size: 20pt; color: #111">Find by:</p>
<div py:for="aspect in aspects">
  <p py:content="'%s:' % (aspect.name,)" class="engal_tag engal_tagaspect_${aspect.short_name}">Location:</p>
  <p py:if="aspect.tags.count()" class="engal_tag_list"><span py:for="tag in aspect.tags[:5]" py:content="tag.name + ', '" /> ... </p>
</div>
</div>

</body>
</html>
