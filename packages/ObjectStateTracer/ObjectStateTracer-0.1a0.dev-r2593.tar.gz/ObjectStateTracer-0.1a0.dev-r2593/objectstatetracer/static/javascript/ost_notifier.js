OSTNotifier = Class.create()

OSTNotifier.prototype.initialize = 
function(container, options) {
    if (window.parent && window.parent.ost_notifier && window != window.parent) {
        // prevent notification windows on iframes from spawning
        return false;
    }
    
    window.ost_notifier = this;
    
    this.container = $(container);
    this.close_button = $(container + '_close');
    this.notification_link = $(container + '_notification');
    this.options = Object.extend({}, options || {});
    
    Element.setStyle(this.container, {'right': '0.5em', 'bottom': '0.5em',
                                      'z-index': '10'});
    
    hide_container = function () {
        this.container.hide();
    }.bind(this);
    Event.observe(this.close_button, 'click', hide_container)
    
    show_pendings = function () {
        var win = new Window('ost_notifier_' + new Date().getTime(),
                             {'width': 900, 'height': 500,
                              'url': this.options.pendings_url, 
                              'className': 'alphacube',
                              'hideEffect': Element.hide, 
                              'showEffect': Element.show});
        win.setDestroyOnClose();
        win.toFront();
        win.showCenter();
        
        on_close = function(e, e_win) {
            if (e_win == win) {
                this.delayed_check();
            }
        }.bind(this);
        observers = {'onClose': on_close};
        Windows.addObserver(observers);
        
        this.container.hide();
    }.bind(this);
    Event.observe(this.notification_link, 'click', show_pendings);
    
    this.check_pendings();
};

OSTNotifier.prototype.process_request = function(request) {
    var results;
    eval('results = ' + request.responseText);
    
    if (typeof(results) != 'object' &&
        typeof(results['pending']) != 'object') {
        this.delayed_check();
    }
    
    if (results['pending']) {
        this.container.show();
    } else {
        this.delayed_check();
    }
};

OSTNotifier.prototype.delayed_check = function() {
    setTimeout(this.check_pendings.bind(this), 
               this.options.check_interval * 1000);
}

OSTNotifier.prototype.check_pendings = function() {
    var request_options = {method: 'get',
                           onSuccess: this.process_request.bind(this),
                           onFailure: this.delayed_check.bind(this)};
    
    new Ajax.Request(this.options.notifier_url, request_options);
};

function open_state_detail(url, parent) {
    var win = new Window('ost_detail_' + new Date().getTime(),
                            {'width': 850, 'height': 450,
                             'url': url, 'className': 'alphacube',
                             'hideEffect': Element.hide, 
                             'showEffect': Element.show});
    win.setDestroyOnClose();
    win.showCenter();
    
    on_close = function(e, e_win) {
        if (e_win == win) {
            parent.location.href = parent.location.href;
        }
    };
    observers = {'onClose': on_close};
    Windows.addObserver(observers);
}
