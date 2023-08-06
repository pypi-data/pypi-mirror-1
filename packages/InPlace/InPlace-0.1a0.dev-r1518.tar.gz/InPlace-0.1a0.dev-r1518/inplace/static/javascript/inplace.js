var InPlace = Class.create();
InPlace.prototype = {};

InPlace.prototype.initialize = function(dom_id, options) {
    this.options = Object.extend({
      'field': new TextField(),
      'getter': null,
      'setter': null
    }, options || {});
    
    this.target = target = $(dom_id);
    this.target.in_place_edit = this;
    
    // target events
    function mouseover() {
        if (this._last_border) {
            return;
        }
        this._last_border = this.style.border;
        this._last_margin = this.style.margin;
        this.style.border = '1px solid red';
        this.style.margin = '-1px';
    }
    Event.observe(this.target , 'mouseover',
                  mouseover.bindAsEventListener(target));
    this.target._mouseover = mouseover.bind(target);
    
    function mouseout() {
        if (typeof(this._last_border) == 'undefined') {
            return;
        }
        this.style.border = this._last_border;
        this.style.margin = this._last_margin;
        delete(this._last_border);
        delete(this._last_margin);
    }
    Event.observe(target , 'mouseout',
                  mouseout.bindAsEventListener(target));
    this.target._mouseout = mouseout.bind(target);
    Event.observe(target , 'click', this.start_edit.bindAsEventListener(this));
    // end target events
    
    this.field = this.options.field;
    
    // field events
    Event.observe(this.field.element, 'blur', this.stop_edit.bind(this));
    // end field events
    
    this.field.element.style.position = 'absolute';
    this.field.element.style.visibility = 'hidden';
    
    document.body.appendChild(this.field.element);
}

InPlace.prototype.start_edit = function(event) {
    event.stopPropagation(); // prevent other onclicks from firing
    
    this.target._mouseout(); // restores original margin/border before hiding
    
    if (this.options.getter) {
        this.field.set_value(this.options.getter());
    } else {
        // if we didn't get a getter function that means the target's contents
        // is the data
        this.field.set_value(this.target.innerHTML);
    }
    
    pos = Position.cumulativeOffset(this.target);
    this.field.element.style.left = pos[0] + 'px';
    this.field.element.style.top = pos[1] + 'px';
    
    this.target.style.visibility = 'hidden';
    this.field.element.style.visibility = 'visible';
    
    this.field.focus && this.field.focus();
    this.field.start_edit && this.field.start_edit();
}

InPlace.prototype.stop_edit = function() {
    this.field.stop_edit && this.field.stop_edit();
    
    this.target.innerHTML = this.field.get_html();
    
    if (this.options.setter) {
        this.options.setter(this.field.get_value(), this.field.get_html());
    }
    
    this.target.style.visibility = 'visible';
    this.field.element.style.visibility = 'hidden';
}


// BaseField Class
var BaseField = Class.create();
BaseField.prototype = {};
BaseField.prototype.start_edit = function() {};
BaseField.prototype.stop_edit = function() {};
BaseField.prototype.focus = function() {};
BaseField.prototype.get_value = function() {};
BaseField.prototype.get_html = function() {
    alert('error: get_html not implemented'); 
};
BaseField.prototype.set_value = function(value) {
    alert('error: set_value not implemented'); 
};


// TextField Class
var TextField = Class.create();
TextField.prototype = {};
Object.extend(TextField.prototype, BaseField.prototype);

TextField.prototype.initialize = function() {
    this.element = field = document.createElement('input');
    field.setAttribute('type', 'text');
    field.style.textAlign = 'center';
    
    field.update_dimensions = function () {
        this.style.width = (this.value.length / 2) + 2 + 'em';
    }.bind(field);
    
    Event.observe(field, 'keydown', field.update_dimensions);
    
    function on_enter(e) {
        if (e.keyCode == Event.KEY_RETURN) {
            this.blur();
        }
    }
    Event.observe(field, 'keydown', on_enter.bindAsEventListener(field));
}    

TextField.prototype.start_edit = function() {
    this.element.update_dimensions();
    this.element.select();
}

TextField.prototype.focus = function() {
    this.element.focus();
}

TextField.prototype.get_html =
TextField.prototype.get_value = function() {
    return this.element.value;
}

TextField.prototype.set_value = function(value) {
    this.element.value = value;
}


// SingleSelectField Class
var SingleSelectField = Class.create();
SingleSelectField.prototype = {};
Object.extend(SingleSelectField.prototype, BaseField.prototype);

SingleSelectField.prototype.initialize = function(field) {
    this.element = $(field).cloneNode(true);
}

SingleSelectField.prototype.set_value = function(value) {
    this.element.value = value;
}

SingleSelectField.prototype.focus = function() {
    this.element.focus();
}

SingleSelectField.prototype.get_value = function() {
    return this.element.options[this.element.selectedIndex].value;
}

SingleSelectField.prototype.get_html = function() {
    if (this.element.selectedIndex < 0) {
        return '';
    }
    
    return this.element.options[this.element.selectedIndex].text;
}


// MoneyField Class
var MoneyField = Class.create();
MoneyField.prototype = {};
Object.extend(MoneyField.prototype, TextField.prototype);

MoneyField.prototype.initialize = function(options) {
    TextField.prototype.initialize.bind(this)();
    
    this.options = Object.extend({
      'decimal_precision': 2,
      'sign': '$'
    }, options || {});
}

MoneyField.prototype.get_html = function() {
    return this.format_price(this.get_value());
}

MoneyField.prototype.format_price = function(value) {
    var sign = this.options.sign;
    
    if (typeof(sign) == 'function') {
        sign = sign();
    }
    
    return sign + ' ' + number_to_string(parseFloat(value));
}


/* unsupported for the moment, too many problems
   the idea of this was creating the InPlace instance during the 1st
   mouseover over the target
   
InPlace.quickstart = function(target) {
    //FIXME: we should clear the firing event. For example, using onmouseover 
    //       it slowdowns the DOM event.
    target = $(target);
    if (!target.in_place_edit) {
        new InPlace(target);
        //FIXME: firing this event by makes opera to miss mouseout sometimes
        //       leaving the red border. There must be a better way to init
        //       the quickstarted edits. 
        // event = document.createEvent('MouseEvents');
        // event.initEvent('mouseover', true, true);
        // target.dispatchEvent(event);
    }
}*/

