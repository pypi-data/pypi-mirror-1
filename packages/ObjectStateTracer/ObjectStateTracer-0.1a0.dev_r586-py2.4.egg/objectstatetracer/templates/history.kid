<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <link py:for="css in tg_css" py:replace="css.display()" />
    <link py:for="js in tg_js_head" py:replace="js.display()" />
    <title>Object History</title>
</head>

<body>
    <div py:for="js in tg_js_bodytop" py:replace="js.display()" />
    <div py:if="value_of('tg_flash')" style="color: red; font-size: large" py:content="tg_flash"/>
    ${panel.display(object)}
    <div py:for="js in tg_js_bodybottom" py:replace="js.display()" />
</body>

</html>