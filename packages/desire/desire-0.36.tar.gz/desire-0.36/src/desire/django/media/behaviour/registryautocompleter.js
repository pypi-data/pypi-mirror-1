/*extern Autocompleter, suspendAutocompletion */

Autocompleter.Ajax.Registry = Autocompleter.Ajax.Json.extend({

    prefetch: function() {
        if (suspendAutocompletion) {
            console.log("Supressing autocompleter key-response.");
        } else {
            this.parent();
        }
    },

    queryResponse: function(resp) {
        if (suspendAutocompletion) {
            console.log("Supressing autocompleter AJAX callback.");
        } else {
            this.parent(resp);
        }
    }

});


var initAutocompleters = function(){
    $$('input.completer').each( function(el) {
        var indicator = new Element('div', {
            'class': 'autocompleter-loading',
            'styles': {'display': 'none'}
        }).setHTML('').injectAfter(el);
        var registryPath = el.getAttribute('registryPath');
        var completer = new Autocompleter.Ajax.Registry(
            el, 
            autocompleterPath,
            {   
                postVar: 'queryString',
                postData: {'registryPath': registryPath},
                'onRequest': function(el) {
                    indicator.setStyle('display', '');
                },
                'onComplete': function(el) {
                    indicator.setStyle('display', 'none');
                },
                'onFailure': function(el) {
                    indicator.setStyle('display', 'none');
                }
            }
        );
    });
}

window.addEvent('domready', initAutocompleters);

