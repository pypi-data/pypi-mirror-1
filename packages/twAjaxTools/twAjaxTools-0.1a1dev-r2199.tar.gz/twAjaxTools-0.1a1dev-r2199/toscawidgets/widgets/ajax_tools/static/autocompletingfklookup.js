AutoCompletingFKLookupManager = Class.create()

AutoCompletingFKLookupManager.prototype.initialize = 
function(field_id, options) {
    this.id = field_id;
    this.idField = $(field_id);
    this.idField.ajax = this;
    this.textField = $(field_id + '_text');
    
    // Disable IE and FireFox autocomplete on the fields.
    this.idField.setAttribute('autocomplete', 'off');
    this.textField.setAttribute('autocomplete', 'off');
    
    this.spinner = $(field_id + '_spinner');
    this.resultsHolder = $(field_id + '_results');
    
    this.searchController = options.url;
    this.searchParamFor = {'id': options.id_search_param,
                           'text': options.text_search_param};
    this.resultName = options.var_name;
    
    this.options = Object.extend({}, options || {});
    
    this.delayedRequest = null;
    this.specialKeyPressed = false;
    this.focus = null;
    this.lastSearch = '';
    this.lastKey = null;
    this.lastResults = null;
    this.selectedResultRow = 0;
    this.lastSelectedText = '';
    this.lastSelectedID = '';
    
    this.numResultRows = 0;
    this.isShowingResults = false;
    this.sugestionBoxMouseOver = false;
    this.processCount = 0;
    this.hasHiddenValue = false;
    
    // Variable to store extra data for the selected result.
    this.extra_data = {};

    Event.observe(this.textField, 'keyup',
                  this.keyUp.bindAsEventListener(this));
    Event.observe(this.textField, 'keydown',
                  this.keyDown.bindAsEventListener(this));
    
    // Don't try to use Event.observe! DOM events won't be able to prevent 
    // some browsers from submitting the form when the user selects an option
    this.textField.onkeypress = this.keyPress;
    
    Event.observe(this.textField, 'blur',
                  this.textLostFocus.bindAsEventListener(this));
    Event.observe(this.textField, 'focus',
                  this.textGotFocus.bindAsEventListener(this));
    
    Event.observe(this.idField, 'keyup',
                  this.keyUp.bindAsEventListener(this));
    Event.observe(this.idField, 'keydown',
                  this.keyDown.bindAsEventListener(this));
    Event.observe(this.idField, 'blur',
                  this.idLostFocus.bindAsEventListener(this));
    Event.observe(this.idField, 'focus',
                  this.idGotFocus.bindAsEventListener(this));
    
    if (this.idField.value != '') {
        this.doRequest(this.idField, this.idField.value);
    }
};

AutoCompletingFKLookupManager.prototype.textLostFocus = function(event) {
    if (this.focus == this.textField) {
        this.focus = null;
    }
    if (!this.sugestionBoxMouseOver || this.lastKey == 9) {
        // We only clear the suggestion box when the mouse is not
        // over it or when the user pressed tab. So if the user
        // clicked an item we don't delete the table before the
        // onClick event happens
        this.lastKey = null;
        this.clearResults();
        
        // If no id was selected and the text field lost focus, 
        // clear the text in it
        if (!this.idField.value) {
            this.textField.value = '';
        }
        
        // If there's no text on the text field when both fields lost focus
        // we clear the id field too, because it probably points to a non 
        // existant ID.
        if (!this.textField.value) {
            this.idField.value = '';
            this.fire('on_clear');
        }
    }
}

AutoCompletingFKLookupManager.prototype.textGotFocus = function(event) {
    this.focus = this.textField;
    this.lastSearch = '';
}

AutoCompletingFKLookupManager.prototype.idLostFocus = function(event) {
    if (this.focus == this.idField) {
        this.focus = null;
        if (!this.idField.value) {
            this.textField.value = '';
            this.fire('on_clear');
        }
    }
}

AutoCompletingFKLookupManager.prototype.idGotFocus = function(event) {
    this.focus = this.idField;
    this.lastSearch = '';
}

AutoCompletingFKLookupManager.prototype.keyPress = function(event) {
    var event = event || window.event;
    var key = event.keyCode || event.keyCode;
    
    // prevents opera from submiting the form or moving the display
    if (event.keyCode == Event.KEY_RETURN) {
        return false;
    }
    return true;
}

AutoCompletingFKLookupManager.prototype.keyDown = function(event) {
    var event = event || window.event;
    var key = event.keyCode || event.keyCode;
    this.lastKey = key;
    
    // enter, escape, up, down
    if (key == Event.KEY_RETURN ||
        key == Event.KEY_ESC ||
        key == Event.KEY_UP ||
        key == Event.KEY_DOWN ||
        key == Event.KEY_TAB) {
        this.specialKeyPressed = true;
    } else {
        this.specialKeyPressed = false;
    }
    
    switch(key) {
        case Event.KEY_RETURN:
            if (this.lastResults && this.lastResults[this.selectedResultRow]) {
                var result = this.lastResults[this.selectedResultRow];
                this.select(result[this.options.id_result_attr],
                            result[this.options.text_result_attr],
                            result[this.options.extra_data_result_attr]);
                this.clearResults();
            }
            break;
        
        case Event.KEY_UP:
            if(this.selectedResultRow > 0) {
                this.selectedResultRow--;
            }
            this.updateHighLightedResult();
            break;
        
        case Event.KEY_DOWN:
            var num_results = this.lastResults.length;
            if (this.selectedResultRow < num_results - 
                (this.selectedResultRow == null ? 0 : 1)) {
                if (this.selectedResultRow == null) {
                    this.selectedResultRow = 0;
                } else {
                    this.selectedResultRow++;
                }
            }
            this.updateHighLightedResult();
            break;
    }
    
    if (this.focus == this.textField && key == Event.KEY_TAB) {
        // Let the browser switch fields if the text field is on focus
        // and the tab key is pressed (because it's the rightmost one).
        return true;
    }
    
    return !this.specialKeyPressed;
}

AutoCompletingFKLookupManager.prototype.keyUp = function(event) {
    // Stop processing if key wasn't pressed on any of the fields
    if (!this.focus) {
        return false;
    }
    
    // Stop processing if a special key has been pressed.
    // Or if the last search requested the same string
    if (this.specialKeyPressed) {
        return false;
    }
    
    // Stop processing if nothing changed (probably some key combination that
    // didn't change the text
    if (this.textField.value == this.lastSelectedText &&
        this.idField.value == this.lastSelectedID) {
        return false;
    }
    
    // Pressing a key on a field automatically clears the other
    if (this.focus == this.idField) {
        this.textField.value = '';
    } else {
        this.idField.value = '';
    }
    
    // If field's value is empty we don't need to schedule a request.
    // We have to clear the list.
    if (!this.focus.value) {
        if (this.delayedRequest) {
            clearTimeout(this.delayedRequest);
        }
        this.lastSearch = '';
        this.clearResults();
        return false;
    }
    
    // Cancel the current request if there's one
    if (this.delayedRequest) {
        clearTimeout(this.delayedRequest);
    }
    
    var currentFocus = this.focus;
    var currentValue = this.focus.value;
    doDelayedRequest = function (event) {
        this.doRequest(currentFocus, currentValue);
    }.bind(this);
    
    // Do the search
    this.delayedRequest = setTimeout(doDelayedRequest, 300);
    
    return true;
}

AutoCompletingFKLookupManager.prototype.doRequest = function(focus, value) {
    if (focus == this.textField && this.focus != this.textField) {
        // We cancel the textField lookups if it lost focus
        return false;        
    }
    
    this.delayedRequest = null;
    this.processCount++;
    this.spinner.show();
    this.lastSearch = value;
    
    var params = $H({'tg_format': 'json',
                     'tg_random' : new Date().getTime()});
    
    var search_param_name = 'text';
    if (focus == this.idField) {
        search_param_name = 'id';
    }
    params[this.searchParamFor[search_param_name]] = value;
    
    var onSucess = function(request) {
        this.requestOk(request, focus, value);
    };
    
    this.fire('before_search');
    
    if (this.options.extra_search_params) {
       params = params.merge(this.options.extra_search_params);
    }
    
    var request_options = {method: 'post', parameters: params.toQueryString(),
                           onSuccess: onSucess.bind(this),
                           onFailure: this.requestFailed.bind(this)};
    
    new Ajax.Request(this.searchController, request_options);
}

AutoCompletingFKLookupManager.prototype.requestFailed = function(request) {
    this.processCount--;
    if (this.processCount <= 0) {
        this.spinner.hide();
    }
    
    alert('There was a problem with the request (code: ' + 
          request.status + ' "' + request.statusText + '")');
}

AutoCompletingFKLookupManager.prototype.requestOk = 
function(request, focus, value) {
    // processes the request, prepares the data, and calls displayResults
    
    this.processCount--;
    if (this.processCount <= 0) {
        this.spinner.hide();
    }
    
    var results;
    eval('results = ' + request.responseText);
    
    if (typeof(results) != 'object' &&
        typeof(results[this.resultName]) != 'object') {
         alert('There was a problem processing the request.');
    }
    
    this.lastResults = results[this.resultName];
    
    if (focus == this.idField) {
        var result = this.lastResults[0];
        if (result[this.options.id_result_attr]) {
            this.select(result[this.options.id_result_attr],
                        result[this.options.text_result_attr],
                        result[this.options.extra_data_result_attr]);
        } else {
            this.textField.value = '';
        }
        return true;
    } else {
        this.displayResults();
    }
}

AutoCompletingFKLookupManager.prototype.displayResults = function() {
    // if the fields lost focus during the query, we don't display the results
    if (!this.focus) {
        return false;
    }
    
    var table = document.createElement('table');
    table.className = 'autoTextTable';
    var tbody = document.createElement('tbody');
    table.appendChild(tbody);
    
    this.selectedResultRow = 0;
    
    // create the rows for each result
    var counter = 0;
    this.lastResults.each(function(result) {
        var tr = document.createElement('tr');
        var td = document.createElement('td');
        tr.appendChild(td);
        
        var row_id = counter++;
        
        tr.className = 'autoTextNormalRow';        
        
        Event.observe(tr, 'mouseover', function() {
            this.selectedResultRow = row_id;
            this.updateHighLightedResult();
            this.sugestionBoxMouseOver = true;
        }.bind(this));
        
        Event.observe(tr, 'click', function() {
            p = {};
            p.keyCode = 13;
            this.keyDown(p);
        }.bind(this));
        
        Event.observe(tr, 'mouseout', function() {
            this.sugestionBoxMouseOver = false;
        });
        
        var text = result[this.options.text_result_attr];        
        td.appendChild(document.createTextNode(text));
        tbody.appendChild(tr);
    }.bind(this));
    
    pos = Position.positionedOffset(this.textField);
    //pos = Position.cumulativeOffset(this.textField);
    
    this.resultsHolder.style.left = pos[0] + 'px';
    this.resultsHolder.style.top = (pos[1] + this.textField.offsetHeight) + 'px';
    
    if (this.resultsHolder.firstChild) {
        this.resultsHolder.replaceChild(table, this.resultsHolder.firstChild);
    } else {
        this.resultsHolder.appendChild(table);
    }
    
    this.updateHighLightedResult();    
}

AutoCompletingFKLookupManager.prototype.updateHighLightedResult = 
function(request) {
    // TODO: Add code to move the cursor to the end of the line
    
    if (!this.resultsHolder.firstChild ||
        !this.resultsHolder.firstChild.firstChild) {
        return false;
    }
    
    var counter = 0;
    $A(this.resultsHolder.firstChild.firstChild.childNodes).each(function(row) {
        if (this.selectedResultRow == counter++) {
            row.className = 'autoTextSelectedRow';
        } else {
            row.className = 'autoTextNormalRow';
        }
    }.bind(this));
}

AutoCompletingFKLookupManager.prototype.clearResults = function(request) {
    if (this.resultsHolder.firstChild) {
        this.resultsHolder.removeChild(this.resultsHolder.firstChild);
    }
}

AutoCompletingFKLookupManager.prototype.select = function(id, text, extra_data) {
    // Sets the data when an option is selected
    this.idField.value = this.lastSelectedID = id;
    this.textField.value = this.lastSelectedText = text;
    
    // Fire a change event on the ID field to emulate a direct change there
    event = document.createEvent('HTMLEvents');
    event.initEvent('change', true, false); 
    this.idField.dispatchEvent(event);
    
    if (extra_data) {
        this.extra_data = extra_data;
    }
    
    // Call the on_select hook
    this.fire('on_select');
}

AutoCompletingFKLookupManager.prototype.fire = function(event) {
    // This method fires the user hooks
    
    event = this.options[event];
    
    if (!event) {
        return false;
    }
    
    if(typeof(event) == 'function') {
        event(this);
    } else {
        eval(event);
    }
}

