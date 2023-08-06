<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">

<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
    <meta py:replace="item[:]"/>
    <meta name="siteinfo" content="turbokid"/>
</head>

<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()">
    <div>top</div>
    <div py:replace="[item.text]+item[:]"/>
    <div>bottom</div>
</body>

</html>
