<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="sitetemplate">
<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
    <meta py:replace="item[:]" name="description" content="master template"/>
</head>
<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()">
    <div py:replace="[item.text]+item[:]">page content</div>
</body>
</html>
