<div py:if="show" id="${name}" class="ost_menu"
     xmlns:py="http://purl.org/kid/ns#">
    <div class="header">
        Tracing
    </div>
    <div id="${name}_pending_changes" class="pending_changes">
        <script type="text/javascript">
            function ost_window(url) {
                var ost_win = new Window('ost_win_' + new Date().getTime(),
                                        {'width': 800, 'height': 500,
                                         'url': url, 'className': 'alphacube'});
                ost_win.setDestroyOnClose();
                ost_win.showCenter();
            }
        </script>
        
        <div py:if="value_of('mod_history_url')">
            <a href="javascript:ost_window('${mod_history_url}')">
                Modification History
            </a>
        </div>
        
        <div py:if="value_of('pending_changes_url')">
            <a href="javascript:ost_window('${pending_changes_url}')">
                ${pending_changes.count()} Pending Change(s)
            </a>
            <span class="alert">!</span>
        </div>
    </div>
</div>