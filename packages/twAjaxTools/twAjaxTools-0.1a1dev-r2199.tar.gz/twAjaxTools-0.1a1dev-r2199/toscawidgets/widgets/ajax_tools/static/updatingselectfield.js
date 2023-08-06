UpdatingSelectFieldManager = Class.create()

UpdatingSelectFieldManager.prototype.initialize = 
function(field_id, options) {
    this.field = $(field_id);
    this.field.ajax = this;
    this.spinner = $(field_id + '_spinner');
    this.watched = $H();
    this.options = Object.extend({
        'filter_params': $H()
    }, options || {});
    
    Event.observe(window, 'load', this.first_fetch.bind(this));
};

UpdatingSelectFieldManager.prototype.first_fetch = function() {
    this.watched.keys().each(function(id) {
        id = $(id);
        this.options.filter_params[id.name] = Form.Element.getValue(id);
    }.bind(this));
    this.update();
}

UpdatingSelectFieldManager.prototype.watch = function(id) {
    Event.observe($(id), 'change', this.watcher.bindAsEventListener(this));
    this.watched[$(id).id] = true;
}

UpdatingSelectFieldManager.prototype.watcher = function(e) {
    var element = $(e.target.id);
    
    this.options.filter_params[element.name] = Form.Element.getValue(element);
    this.update();
}

UpdatingSelectFieldManager.prototype.update = function(extra_params) {
    this.spinner.show();
    
    parameters = $H(this.options.filter_params);
    
    if (extra_params) {
        parameters.merge(extra_params);
    }
    
    var request_options = {method: 'post',
                           parameters: parameters.toQueryString(),
                           onSuccess: this.requestOk.bind(this),
                           onFailure: this.requestFailed.bind(this)};
    
    new Ajax.Request(this.options.controller, request_options);
}

UpdatingSelectFieldManager.prototype.requestOk = function(request) {
    // update the field options
    var results;
    eval('results = ' + request.responseText);
    
    if (typeof(results) != 'object' &&
        typeof(results.options) != 'object') {
         alert('There was a problem processing the request.');
    }
    
    var value_to_index = $H();
    
    this.field.options.length = 0;
    $A(results.options).each(function(opt) {
        var value = opt[0];
        var description = opt[1];
        
        if (!description) {
            description = '';
        }
        
        if (!value) {
            value = '';
        }
        
        option = new Option(description, value);
        if (opt[2]) {
            // Add extra attributes to the option tag
            $H(opt[2]).each(function(i) { 
                option.setAttribute(i[0], i[1]);
            });
        }
        this.field.options.add(option);
        value_to_index[value] = this.field.options.length - 1;
    }.bind(this));
    
    if (this.options.initial_value) {
        this.field.selectedIndex = value_to_index[this.options.initial_value];
        this.options.initial_value = null;
    }
    
    this.spinner.hide();
}

UpdatingSelectFieldManager.prototype.requestFailed = function(request) {
    this.spinner.hide();
    alert('There was a problem with the request (code: ' + 
          request.status + ' "' + request.statusText + '")');
}