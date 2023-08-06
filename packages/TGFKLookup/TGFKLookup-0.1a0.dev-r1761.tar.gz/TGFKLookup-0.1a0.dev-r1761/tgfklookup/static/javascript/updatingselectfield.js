UpdatingSelectFieldManager = Class.create()

UpdatingSelectFieldManager.prototype.initialize = 
function(field_id, options) {
    this.id = field_id;
    this.field = $(field_id);
    this.spinner = $(field_id + '_spinner');
    this.options = Object.extend({}, options || {});
};

UpdatingSelectFieldManager.prototype.update = function() {
    this.spinner.show();
    
    var request_options = {method: 'post',
                           parameters: $H(this.options.filter_params).
                                            toQueryString(),
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
    
    this.field.options.length = 0;
    $A(results.options).each(function(opt) {
        this.field.options.add(new Option(opt[1], opt[0]));
    }.bind(this));
    
    this.spinner.hide();
}

UpdatingSelectFieldManager.prototype.requestFailed = function(request) {
    this.spinner.hide();
    alert('There was a problem with the request (code: ' + 
          request.status + ' "' + request.statusText + '")');
}