<div xmlns:py="http://purl.org/kid/ns#">
    <div id="${id}" class="ost_notifier" style="display: none;">
        <span id="${id}_close" class="close">${G_('Close')}</span>
        <span id="${id}_notification" class="notification">
            ${G_('There are pendings you can authorize')}
        </span>
    </div>
    <script type="text/javascript">
        new OSTNotifier('${id}', ${options});
    </script>
</div>