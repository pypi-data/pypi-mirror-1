/*
* Copyright (c) 2005-2007
* Authors: KSS Project Contributors (see docs/CREDITS.txt)
*
* This program is free software; you can redistribute it and/or modify
* it under the terms of the GNU General Public License version 2 as published
* by the Free Software Foundation.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program; if not, write to the Free Software
* Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
* 02111-1307, USA.
*/

/* Form handling utilities */

kukit.fo = {};

/* form query assembler */

// Prefix constants for dict marshalling, 
//     pattern: %s(dictprefix)%(name)s%(dictseparator)s%(key)s%(dictpostfix)s
// XXX this should be settable
kukit.fo.dictprefix = '';
kukit.fo.dictseparator = '.';
kukit.fo.dictpostfix = ':record';

/*
* class FormQueryElem
*/
kukit.fo.FormQueryElem = function(name, value) {
    this.name = name;
    this.value = value;
};
    
kukit.fo.FormQueryElem.prototype.encode = function() {
    return this.name+ "=" + encodeURIComponent(this.value);
};
    
/*
* class FormQuery
*/
kukit.fo.FormQuery = function() {
    this.l = [];
};

kukit.fo.FormQuery.prototype.appendElem = function(name, value) {
    if (typeof(value) == 'object') {
        // Special marshalling of dicts
        for (var key in value) {
            var qkey = kukit.fo.dictprefix + name + kukit.fo.dictseparator + key + kukit.fo.dictpostfix;
            var elem = new kukit.fo.FormQueryElem(qkey, value[key]);
            this.l.push(elem);
        }
    } else {
        // normal strings
        var elem = new kukit.fo.FormQueryElem(name, value);
        this.l.push(elem);
    }
};

kukit.fo.FormQuery.prototype.encode = function() {
    var poster = [];
      for (var i=0;i < this.l.length;i++) {
        poster[poster.length] = this.l[i].encode();
    }
    return poster.join("&");
};

kukit.fo.FormQuery.prototype.toDict = function() {
    var d = {};
      for (var i=0;i < this.l.length;i++) {
        var elem = this.l[i];
        d[elem.name] = elem.value;
    }
    return d;
};

/* Form data extraction, helpers */

kukit.fo.findContainer = function(node, func) {
    // Starting with the given node, find the nearest containing element
    // for which the given function returns true.
    while (node != null) {
        if (func(node)) {
            return node;
        }
        node = node.parentNode;
    }
    return null;
};

/*
 * class CurrentFormLocator: gets the current form of a target
 *
 */

kukit.fo.CurrentFormLocator = function(target) {
    this.target = target;
};

kukit.fo.CurrentFormLocator.prototype.queryForm = function() {
    // Find the form that contains the target node.
    return kukit.fo.findContainer(this.target, function(node) {
        if (!node.nodeName) {
            return false;
        }
        if (node.nodeName.toLowerCase() == "form") {
            return true;
        } else {
            return false;
        }
    });
};

kukit.fo.CurrentFormLocator.prototype.getForm = function() {
    var form = this.queryForm();
    if (!form) {
        ;;; kukit.logWarning("No form found");
        return null;
    }
    return form;
};

/*
 * class NamedFormLocator: gets the form with a given name
 *
 */

kukit.fo.NamedFormLocator = function(formname) {
    this.formname = formname;
};

kukit.fo.NamedFormLocator.prototype.queryForm = function() {
    // Find the form with the given name.
    return document.forms[this.formname];
};

kukit.fo.NamedFormLocator.prototype.getForm = kukit.fo.CurrentFormLocator.prototype.getForm;

/* methods to take the desired value(s) from the form */

kukit.fo.getValueOfFormElement = function(element) {
    // Returns the value of the form element / or null
    // First: update the field in case an editor is lurking
    // in the background
    kukit.fo.fieldUpdateRegistry.doUpdate(element);
    // Collect the data
    if (element.selectedIndex != undefined) {
	// handle single selects first
	if(!element.multiple){
            if (element.selectedIndex < 0) {
		value="";
            } else {
		var option = element.options[element.selectedIndex];
		value = option.value;
		if (value == "")
                    value = option.text;
            }
	} 
	// Now process selects with the multiple option set
	else {
	    var value = [];
	    for(i=0; i<element.options.length; i++){
		var option = element.options[i];
		if(option.selected){
		    value.push(option.value);
		}
	    }
	    return value;
	}
    } else if (typeof element.length != 'undefined' && typeof element.item != 'undefined' && element.item(0).type == "radio") {
        var radioList = element;
        value = null;
        for (var i=0; i < radioList.length; i++) {
            var radio = radioList.item(i);
            if (radio.checked) {
                value = radio.value;
            }
        }
    } else if (element.type == "radio" || element.type == "checkbox") {
        if (element.checked) {
           value = element.value;
        } else {
            value = null;
        }   
    } else if ((element.tagName.toLowerCase() == 'textarea')
               || (element.tagName.toLowerCase() == 'input' && 
                    element.type != 'submit' && element.type != 'reset')
              ) {
        value = element.value;
    } else {
        value = null;
    }
    return value;
};

kukit.fo.getFormVar = function(locator, name) {
    var form = locator.getForm();
    if (! form)
        return null;
    // Extract the value of a formvar
    var value = null;
    var element = form[name];
    if (element) {
        var value = kukit.fo.getValueOfFormElement(element);
        ;;; if (value != null) {
        ;;;    kukit.logDebug("Form element ("+element.tagName+"): name="+element.name+", value="+value);
        ;;; // } else {
        ;;; //   kukit.logWarning('Form element not harvested: '+element.tagName);
        ;;; }
    ;;; } else {
    ;;;     kukit.logWarning('Form element '+ name + '" not found in form.');
    }
    return value;
};

kukit.fo.getAllFormVars = function(locator, collector) {
    var form = locator.getForm();
    if (! form)
        return collector.result;
    // extracts all elements of a given form
    // the collect_hook will be called wih the name, value parameters to add it
    var elements = form.elements;
    for (var y=0; y<elements.length; y++) {
        var element = elements[y];
        var value = kukit.fo.getValueOfFormElement(element);
        if (value != null) {
            ;;; kukit.logDebug("Form element ("+element.tagName+"): name="+element.name+", value="+value);
            collector.add(element.name, value);
        ;;; // } else {
        ;;; //    kukit.logWarning('Form element not harvested: '+element.tagName);
        }
    }
    return collector.result;
};


/* With editors, there are two main points of handling:

   1. we need to load them after injected dynamically
   2. we need to update the form before we accces the form variables

    Any editor has to register the field on their custody.
    The update handler will be called automatically, when a form
    value is about to be fetched.
*/

/*
* class FieldUpdateRegistry
*/
kukit.fo.FieldUpdateRegistry = function() {
    this.editors = {};
};

kukit.fo.FieldUpdateRegistry.prototype.register = function(node, editor) {
    var hash = kukit.rd.hashnode(node);
    if (typeof(this.editors[hash]) != 'undefined') {
        ;;; kukit.E = 'Double registration of editor update on node.';
        throw kukit.E;
    }
    this.editors[hash] = editor;
    //kukit.logDebug('Registered '+node.name + ' hash=' + hash);
    //Initialize the editor
    editor.doInit();
};

kukit.fo.FieldUpdateRegistry.prototype.doUpdate = function(node) {
    var hash = kukit.rd.hashnode(node);
    var editor = this.editors[hash];
    if (typeof(editor) != 'undefined') {
        editor.doUpdate(node);
        //kukit.logDebug('Updated '+node.name + ' hash=' + hash);
    }
};

kukit.fo.fieldUpdateRegistry = new kukit.fo.FieldUpdateRegistry();


// Registry of the pprovider functions for kssSubmitForm

kukit.fo.pproviderFormRegistry = new kukit.pr.ParamProviderRegistry();

// form, currentForm will provide identical functions do those in normal parameters
// except they return a tuple list, not a dictionary.
// This is needed because duplications and order must be preserved.

kukit.fo.FormPP = function() {};
kukit.fo.FormPP.prototype = {
    /*
    ;;; */
    check: function(args) {
        if (args.length != 1) {
           throw 'form method needs 1 arguments (formname)';
        }
    },
    /*
    */
    eval: function(args, node) {
        return kukit.fo.getAllFormVars(new kukit.fo.NamedFormLocator(args[0]), new kukit.ut.TupleCollector());
    }
};
kukit.fo.pproviderFormRegistry.register('form', kukit.fo.FormPP);

kukit.fo.CurrentFormPP = function() {};
kukit.fo.CurrentFormPP.prototype = {
    /*
    ;;; */
    check: function(args) {
        if (args.length != 0) {
            throw 'currentForm method needs no argument';
        }
    },
    /*
    */
    eval: function(args, node) {
        return kukit.fo.getAllFormVars(new kukit.fo.CurrentFormLocator(node), new kukit.ut.TupleCollector());
    }
};
kukit.fo.pproviderFormRegistry.register('currentForm', kukit.fo.CurrentFormPP);

// If a string is given, that will look like a form lookup,
// ie. identical to form
kukit.fo.pproviderFormRegistry.register('', kukit.fo.FormPP);


/* BBB. To be deprecated at 2007-06-15 */

kukit.fo.getCurrentForm = function(target) {
    ;;; kukit.logWarning('Deprecated kukit.fo.getCurrentForm(target), new kukit.fo.CurrentFormLocator(target).getForm() instead!');
    return new kukit.fo.CurrentFormLocator(target).getForm();
};

kukit.fo.getFormVarFromCurrentForm = function(target, name) {
    ;;; kukit.logWarning('Deprecated kukit.fo.getFormVarFromCurrentForm(target, name), use kukit.fo.getFormVar(new kukit.fo.CurrentFormLocator(target), name) instead!');
    return kukit.fo.getFormVar(new kukit.fo.CurrentFormLocator(target), name);
};

kukit.fo.getFormVarFromNamedForm = function(formname, name) {
    ;;; kukit.logWarning('Deprecated kukit.fo.getFormVarFromNamedForm(formname, name), use kukit.fo.getFormVar(new kukit.fo.NamedFormLocator(formname), name) instead!');
    return kukit.fo.getFormVar(new kukit.fo.NamedFormLocator(formname), name);
};

kukit.fo.getAllFormVarsFromCurrentForm = function(target) {
    ;;; kukit.logWarning('Deprecated kukit.fo.getAllFormVarsFromCurrentForm(target), use kukit.fo.getAllFormVars(new kukit.fo.CurrentFormLocator(target), new kukit.ut.DictCollector()) instead!');
    return kukit.fo.getAllFormVars(new kukit.fo.CurrentFormLocator(target), new kukit.ut.DictCollector());
};

kukit.fo.getAllFormVarsFromNamedForm = function(formname) {
    ;;; kukit.logWarning('Deprecated kukit.fo.getAllFormVarsFromNamedtForm(formname), use kukit.fo.getAllFormVars(new kukit.fo.NamedFormLocator(formname), new kukit.ut.DictCollector()) instead!');
    return kukit.fo.getAllFormVars(new kukit.fo.NamedFormLocator(formname), new kukit.ut.DictCollector());
};

