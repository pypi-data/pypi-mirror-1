
var AjaxFormManager = Class.create();

AjaxFormManager.prototype = {};
AjaxFormManager.prototype.initialize = function(id, options) {
    this.form = $(id);
    this.form.ajax = this;
    
    this.options = options || {};
    
    // Setup the hidden iframe we use to do asynchronous requests.
    var iframe_name = this.form.id + '__iframe';
    var i_hate_internet_explorer = true;
    if(i_hate_internet_explorer) {
        // I hate Internet Explorer so much. For some reason the form won't
        // submit to iframes created via DOM. Lost 30'. Thanks IE.
        iframeHTML = '<iframe id="' + iframe_name + '" ';
        iframeHTML +='name="' + iframe_name + '" ';
        iframeHTML +='style="display: none;">';
        iframeHTML +='</iframe>';
        this.form.innerHTML += iframeHTML;
        this.iframe = $(iframe_name);
    } else {
        this.iframe = document.createElement('iframe');
        this.iframe.id = iframe_name;
        this.iframe.name = iframe_name;
        this.iframe.hide();
        document.body.appendChild(this.iframe);
    }
    
    this.form.target = this.iframe.name;
    
    // Add an extra field containing form id to tell the ajax connector who to
    // call back.
    this.id_field = document.createElement('input');
    this.id_field.type = 'hidden';
    this.id_field.name = '_ajax_form_parent_id';
    this.id_field.value = this.form.id;
    this.form.appendChild(this.id_field);
    
    this.submit = $(this.form.id + '_submit');
    
    // js_function('xxx').ajax.submitted() <- doesn't work
    // Workaround: js_function('xxx').get_ajax().submitted()
    this.form.get_manager = function() { return this; }.bind(this);
    
    // Poor man's spinner, use the submit error container to insert some text
    // TODO: change it for an image
    this.spinner = $(this.form.id + '_submit_error');
    this.spinner.hide();
    this.spinner.innerHTML = 'Submitting...';
    
    Event.observe(this.form, 'submit',  function() { 
        this.spinner.show(); 
        this.submit.disable();
    }.bind(this));
};


AjaxFormManager.prototype.reset_form = function() {
    Form.reset(this.form);
    this.id_field.value = this.form.id;
}

AjaxFormManager.prototype.submitted = function(response) {
    this.set_form_errors({}); // clear errors
    
    this.spinner.hide();
    this.submit.enable();
    
    failed = false;
    
    switch (response.status) { 
        case 'OK':
                if (this.options.clear_after_submit) {
                    this.reset_form();
                }
                this.fire_event('on_success');
                break;
        case 'FAILED_VALIDATION':
                this.set_form_errors(response.form_errors);
                failed = true;
                break;
        default:
                failed = true;
                alert('Error processing purchase order. Status (' + 
                                response.status + ')');
    }
    
    if (failed) {
        this.fire_event('on_failure');
    }
    
    this.fire_event('on_complete');
    
    if (!this.options.ignore_flash && response.flash) {
        alert(response.flash);
    }
    
    if (!this.options.ignore_redirects && response.redirect) {
        window.location.href = response.redirect;
    }
};


AjaxFormManager.prototype.set_form_errors = function (errors) {
    if (!errors) {
        errors = {};
    }
    
    if (typeof(errors) == 'string') {
        alert(errors);
        errors = {}; // clear fields errors
    }
    
    Form.getElements(this.form).each(function(element) {
        if (element.type == 'submit' || element.type == 'hidden') {
                return false;
        }
        
        error_container = $(element.id + '_error');
        
        if (!error_container) {
            if (errors[element.name]) {
                alert(element.id + ': ' + errors[element.name]);
            }
            return false;
        }
        
        if (errors[element.name]) {
            error_container.innerHTML = errors[element.name];
        } else {
            error_container.innerHTML = '';
        }
    });
}


AjaxFormManager.prototype.fire_event = function(event) {
    if (this.options[event]) {
        _event = this.options[event];
        try {
            if (typeof(_event) == 'function') {
                _event();
            } else {
                eval(_event);
            }
        } catch (err) {
            alert('Error firing ' + event + ' (' + err + ')');
        }
    }
};


