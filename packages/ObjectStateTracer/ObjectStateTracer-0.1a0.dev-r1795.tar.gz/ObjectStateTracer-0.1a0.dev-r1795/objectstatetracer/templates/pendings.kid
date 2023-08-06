<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">

<head>
    <title>Pending States</title>
    <script type="text/javascript">
    <![CDATA[
        function local_open_state_detail(url) {
            var win = new Window('ost_detail_' + new Date().getTime(),
                                    {'width': 800, 'height': 500,
                                     'url': url, 'className': 'alphacube',
                                     'hideEffect': Element.hide, 
                                     'showEffect': Element.show});
            win.setDestroyOnClose();
            win.showCenter();
        }
        
        function open_state_detail(url) {
            if (window.parent != window && window.parent.open_state_detail) {
                window.parent.open_state_detail(url, window);
            } else {
                local_open_state_detail(url);
            }
        }
        
        function soft_refresh() {
            window.location.href = window.location.href;
        }
    ]]>
    </script>
</head>

<body>
    <a href="javascript: soft_refresh();" style="font-size: small">
        ${_('Refresh')}
    </a>
    ${panel.display(pendings)}
</body>

</html>