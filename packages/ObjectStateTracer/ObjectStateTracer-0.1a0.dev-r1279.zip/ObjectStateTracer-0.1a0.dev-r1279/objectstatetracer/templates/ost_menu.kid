<div id="${name}" class="ost_menu"
     xmlns:py="http://purl.org/kid/ns#">
    <div class="header">
        Tracing
    </div>
    <div id="${name}_pending_changes" class="pending_changes">
        <script type="text/javascript">
            function ost_window(url) {
                var win = new Window('ost_win_' + new Date().getTime(),
                                        {'width': 800, 'height': 500,
                                         'url': url, 'className': 'alphacube',
                                         'hideEffect': Element.hide, 
                                         'showEffect': Element.show});
                win.setDestroyOnClose();
                win.showCenter();
                
                on_close = function(e, e_win) {
                    if (e_win == win) {
                        window.location.href = window.location.href;
                    }
                };
                observers = {'onClose': on_close};
                Windows.addObserver(observers);
            }
        </script>
        
        <div py:if="value_of('creation_history_url')">
            <a href="javascript:ost_window('${creation_history_url}')">
                ${_('Creation History')}
            </a>
        </div>
        
        <div py:if="value_of('pending_creations_url')">
            <a href="javascript:ost_window('${pending_creations_url}')">
                ${pending_creations.count()} 
                <span>
                    ${_('Pending Creations(s)')}
                </span>
            </a>
            <span class="alert">!</span>
        </div>

        <div py:if="value_of('mod_history_url')">
            <a href="javascript:ost_window('${mod_history_url}')">
                ${_('Modification History')}
            </a>
        </div>
        
        <div py:if="value_of('pending_changes_url')">
            <a href="javascript:ost_window('${pending_changes_url}')">
                ${pending_changes.count()}
                <span>
                    ${_('Pending Change(s)')}
                </span>
            </a>
            <span class="alert">!</span>
        </div>

    </div>
</div>