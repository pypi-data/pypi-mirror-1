// master.js - scanbooker behaviour control

/*extern $, $$, $each, Event autoappendPath autodeletePath */

var DEBUG = true;

var suspendAutocompletion = false;

// Allow debugging code to stick around:
if (!DEBUG || !window.console || !console.firebug) {
    var names = ["log", "debug", "info", "warn", "error", "assert", "dir",
                 "dirxml", "group", "groupEnd", "time", "timeEnd", "count",
                 "trace", "profile", "profileEnd"];

    window.console = {};
    for (var i = 0; i < names.length; i += 1) { 
        window.console[names[i]] = function () {};
    }
}

var greyed = {
    'loginform-username': '<username>',
    'loginform-password': 'password',
    'project-search-terms': 'Search terms...',
    'user-search-terms': 'Search terms...',
    'processes-completer': 'Add process...',
    'products-completer': 'Add product...',
    'goals-completer': 'Add goal...',
    'events-completer': 'Add event...',
    'walks-completer': 'Add walk...',
    'collections-completer': 'Add collection...',
    'responses-completer': 'Add story...',
    'causes-completer': 'Add story...',
    'raises-completer': 'Add event...',
    'handles-completer': 'Add event...',
    'requirements-completer': 'Add requirement...',
    'stories-completer': 'Add story...',
};

var table_ids = [
    'register-table',
    'processes-table',
    'products-table',
    'goals-table',
    'events-table',
    'walks-table',
    'collections-table',
    'responses-table',
    'causes-table',
    'raises-table',
    'handles-table',
    'requirements-table',
    'stories-table',
];

var initTicketCompleteLinks = function () {
    $$('a.ticket-completer').each(function (elem) {
        elem.addEvent('click', function (ev) {
            ev = new Event(ev);
            ev.stop();
            var ticketPath = this.getProperty('href');
            if (! ticketPath) {
                console.error("No ticket path in link (set the href).");
                return;
            }
            var registryPath = this.getProperty('id');
            if (! registryPath) {
                console.error("No registry path in link (set the id).");
                return;
            }
            if (ticketPath) {
                var iframeHTML = '';
                iframeHTML += '<big>1. Create or modify ticket for requirement.</big>';
                iframeHTML += '<iframe src="'+ticketPath+'" width="100%" height="230px"></iframe>';
                iframeHTML += '<br />';
                iframeHTML += '<br />';
                iframeHTML += '<br /><big>2. Close dialog, or fix and save ticket location.</big>';
                iframeHTML += '<br />';
                iframeHTML += '<form id="ticket-dialog-form"">';
                iframeHTML += '<input id="ticket-url-input" type="text" size="100" name="ticket-url" value="'+ticketPath+'">';
                iframeHTML += '<input id="registry-path-input" type="hidden" size="100" name="registry-path" value="'+registryPath+'">';
                iframeHTML += '<br />';
                iframeHTML += '<input type="submit" value="Save &raquo;">';

                iframeHTML += '</form>';
                var modal = new AscModal({
                    addCloseBtn: false,
                    popOpacity: 1
                });
                modal.set_contents(iframeHTML, 'n');
                var ticketDialogForm = $('ticket-dialog-form');
                ticketDialogForm.addEvent('submit', function (ev) {
                    ev = new Event(ev);
                    ev.stop();
                    var ticketUrlInput = $('ticket-url-input');
                    var registryPathInput = $('registry-path-input');
                    this.hide();
                    // Save ticketUrl.
                    var ajaxData = {};
                    ajaxData['attrName'] = 'ticketUrl';
                    ajaxData['attrValue'] = ticketUrlInput.getProperty('value');
                    ajaxData['registryPath'] = registryPathInput.getProperty('value');
                    var ajaxPath = attrupdatePath;
                    doAjaxRequest(ajaxPath, ajaxData);
                }.bind(modal));
                modal.show();
            }
        }.bind(elem));
    });
};

var initDissociateLinks = function () {
    $$('a.dissociate').each(function (elem) {
        elem.addEvent('click', function (ev) {
            ev = new Event(ev);
            ev.stop();
            var registryPath = this.getProperty('href');
            if (registryPath) {
                var ajaxData = {};
                ajaxData['registryPath'] = registryPath;
                var ajaxPath = autodeletePath;
                doAjaxRequest(ajaxPath, ajaxData);
            }
        }.bind(elem));
    });
};

var doAjaxRequest = function (ajaxPath, ajaxData) {
    console.log('doAjaxRequest: ajaxPath, ajaxData:');
    console.log(ajaxPath);
    console.log(ajaxData);
    var ajax = new Ajax(ajaxPath, {autoCancel: true});
    ajax.addEvent('onComplete', function (response) {
        if (response == '"OK"') {
            doFreshTables();
        } else {
            setCursorAuto();
        }
    });
    ajax.addEvent('onFailure', function () {
        setCursorAuto();
    });
    setCursorWait();
    ajax.request(ajaxData);
};

var doFreshTables = function () {
    var href = unescape(window.location.pathname);
    var ajax2 = new Ajax(href, {method: 'get', autoCancel: true});
    ajax2.addEvent('onComplete', fillTables);
    ajax2.request();
};

var fillTables = function (html) {
    var newDoc = window.document.createElement('document');
    newDoc.innerHTML = html;
    elems = newDoc.getElements('div');
    elems.each(function (elem, index) {
        id = elem.getAttribute('id');
        if (id && table_ids.contains(id)) {
            $(id).innerHTML = elem.innerHTML;
        };
    });
    initDissociateLinks();
    initTicketCompleteLinks();
    setCursorAuto();
};

var setCursorAuto = function () {
    document.body.style.cursor = "auto";
};

var setCursorWait = function () {
    document.body.style.cursor = "wait";
};

window.addEvent('domready', function () {
    $$('.box').addRoundedCorners();

    $each(greyed, function (txt, id) { 
        var elem = $(id);
        // Set up elements as greyed to start with.
        if (elem) { elem.toggleGreyed(greyed); }
    });

    $$('input').each(function (elem) {
        elem.addEvents({
            focus: elem.toggleGreyed.pass(greyed, elem),
            blur: elem.toggleGreyed.pass(greyed, elem)
        });
    });
    $$('input.completer').each(function (elem) {
        elem.getParent().addEvent(window.ie ? 'keydown' : 'keypress', function(ev) {
            ev = new Event(ev);
            if (ev.key && !ev.shift && ev.key == 'enter') {
                ev.stop();
                var completedString = this.getProperty('value');
                this.setProperty('value', '');
                var registryPath = this.getProperty('registryPath');
                if (completedString && registryPath) {
                    var ajaxData = {};
                    ajaxData['completedString'] = completedString;
                    ajaxData['registryPath'] = registryPath;
                    ajaxData['targetAttribute'] = 'description';
                    var ajaxPath = autoappendPath;
                    doAjaxRequest(ajaxPath, ajaxData);
                }
            }
        }.bind(elem));
    });
    initDissociateLinks();
    initTicketCompleteLinks();
});
// vim:ts=4:sw=4:sts=4:et:
