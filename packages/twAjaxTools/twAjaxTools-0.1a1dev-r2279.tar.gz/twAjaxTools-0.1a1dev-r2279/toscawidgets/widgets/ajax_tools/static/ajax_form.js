
var AjaxFormManager = Class.create();

AjaxFormManager.prototype = {};
AjaxFormManager.prototype.initialize = function(id, options) {
    this.form = $(id);
    this.form_id = this.form.getAttribute('id');
    this.form.ajax = this;
    
    this.options = options || {};
    
    // Setup the hidden iframe we use to do asynchronous requests.
    var iframe_name = this.form_id + '__iframe';
    var i_hate_internet_explorer = true;
    if(i_hate_internet_explorer) {
        // I hate Internet Explorer so much. For some reason the form won't
        // submit to iframes created via DOM. Lost 30'. Thanks IE.
        iframeHTML = '<iframe id="' + iframe_name + '" ';
        iframeHTML +='name="' + iframe_name + '" ';
        
        // Update 04-12-2007, IE6 gives a warning (show nonsecure items - Y/N)
        // when an IFRAME is added without a src="".
        iframeHTML +='src="/toscawidgets/resources/toscawidgets.widgets.' +
                           'ajax_tools.widgets/static/blank.html" ';
        
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
    this.id_field.value = this.form_id;
    this.form.appendChild(this.id_field);
    
    this.submit_button = $(this.form_id + '_submit');
    
    // Poor man's spinner, use the submit error container to insert some text
    // TODO: change it for an image
    this.spinner = $(this.form_id + '_submit_error');
    this.spinner.hide();
    this.spinner.innerHTML = 'Submitting...';
    
    Event.observe(this.form, 'submit',  function() { 
        this.spinner.show(); 
        this.submit_button.disabled = true;
    }.bind(this));
};


AjaxFormManager.prototype.reset_form = function() {
    Form.reset(this.form);
    
    // Set the ID again because Form.reset clears the hidden field.
    this.id_field.value = this.form_id;
}

AjaxFormManager.prototype.submitted = function(response) {
    this.clear_form_errors();
    
    this.spinner.hide();
    this.submit_button.disabled = false;
    var failed = false;
    
    switch (response.status) { 
        case 'OK':
                if (this.options.clear_after_submit) {
                    this.reset_form();
                }
                this.fire_event('on_success', response);
                break;
        case 'FAILED_VALIDATION':
                this.set_form_errors(response.form_errors);
                failed = true;
                break;
        case 'IDENTITY_FAILURE':
                if (!this.options.ignore_identity_flash && 
                     response.identity_flash) {
                    alert(response.identity_flash);
                }
                this.fire_event('on_identity_failure', response);
                failed = true;
                break;
        default:
                failed = true;
                alert('Error processing purchase order. Status (' + 
                                response.status + ')');
    }
    
    if (failed) {
        this.fire_event('on_failure', response);
    }
    
    this.fire_event('on_complete', response);
    
    if (!this.options.ignore_flash && response.flash) {
        alert(response.flash);
    }
    
    if (!this.options.ignore_redirects && response.redirect) {
        window.location.href = response.redirect;
    }
};


AjaxFormManager.prototype.display_error = function (id, error) {
    if (typeof(error) != 'string') {
        $H(error).each(function(i) {
            this.display_error(id + '_' + i[0], i[1]);
        }.bind(this));
        return true;
    }
    
    var error_id = this.form_id + '_' + id + '_error';
    var error_container = $(error_id);
    
    if (error_container) {
        error_container.innerHTML = error;
        Element.show(error_container);
    } else {
        // if we can't find an error container we show it in an alert
        alert(this.form_id + '_' + id + ': ' + error);
    }
};


AjaxFormManager.prototype.set_form_errors = function (errors) {
    if (!errors) {
        errors = {};
    }
    
    if (typeof(errors) == 'string') {
        alert(errors);
        return true;
    }
    
    // display errors
    $H(errors).each(function(i) {
        this.display_error(i[0], i[1]);
    }.bind(this));
};


AjaxFormManager.prototype.clear_form_errors = function() {
    Form.getElements(this.form).each(function(element) {
        if (element.type == 'submit' || element.type == 'hidden') {
                return false;
        }
        
        var error_container = $(element.id + '_error');
        
        if (error_container) {
            error_container.innerHTML = '';
            Element.hide(error_container);
        }
    });
};


AjaxFormManager.prototype.fire_event = function(event, response) {
    if (this.options[event]) {
        _event = this.options[event];
        try {
            if (typeof(_event) == 'function') {
                _event(response);
            } else {
                eval(_event);
            }
        } catch (err) {
            alert('Error firing ' + event + ' (' + err + ')');
        }
    }
};


