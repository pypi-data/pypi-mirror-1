/*
* Copyright (c) 2005-2006
* Authors:
*   Godefroid Chapelle <gotcha@bubblenet.be>
*   Florian Schulze <florian.schulze@gmx.net>
*   Balázs Reé <ree@greenfinity.hu>
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
kukit.fo.dictprefix = ''
kukit.fo.dictseparator = '.'
kukit.fo.dictpostfix = ':record'

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

kukit.fo.getCurrentForm = function(target) {
    // Find the form that contains the target node.
    return kukit.fo.findContainer(target, function(node) {
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

kukit.fo.getValueOfFormElement = function(element) {
    // Returns the value of the form element / or null
    // First: update the field in case an editor is lurking
    // in the background
    kukit.fo.fieldUpdateRegistry.doUpdate(element);
    // Collect the data
    if (element.selectedIndex != undefined) {
        if (element.selectedIndex < 0) {
            value="";
        } else {
            var option = element.options[element.selectedIndex];
            value = option.value;
            if (value == "")
                value = option.text;
        }
    } else if (element.type == "checkbox") {
        value = element.checked;
    } else if (element.type == "radio") {
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

kukit.fo.getFormVar = function(form, name) {
    // Extract the value of a formvar, from a given form
    var value = null;
    var element = form[name];
    if (element) {
        var value = kukit.fo.getValueOfFormElement(element);
        if (value == null) {
            kukit.logWarning('Form element not harvested: '+element.tagName);
        } else {
            kukit.logDebug("Form element ("+element.tagName+"): name="+element.name+", value="+value);
        }
    } else {
        kukit.logWarning('Form element '+ name + '" not found in form.');
    }
    return value;
};

kukit.fo.getAllFormVars = function(form) {
    // extracts all elements of a given form
    var data = {};
    var elements = form.elements;
    for (var y=0; y<elements.length; y++) {
        var element = elements[y];
        var value = kukit.fo.getValueOfFormElement(element);
        if (value == null) {
            kukit.logWarning('Form element not harvested: '+element.tagName);
        } else {
            kukit.logDebug("Form element ("+element.tagName+"): name="+element.name+", value="+value);
            data[element.name] = value;
        }
    }
    return data;
};

/* Form data extraction, frontend */

kukit.fo.getFormVarFromCurrentForm = function(target, name) {
    // Just get one formvar, from the form that contains the target node
    var form = kukit.fo.getCurrentForm(target);
    if (!form) {
        kukit.logWarning("No form found");
        return null;
    }
    return kukit.fo.getFormVar(form, name);
};

kukit.fo.getFormVarFromNamedForm = function(formname, name) {
    // Just get one formvar, from the named form 
    var form = document.forms[formname];
    if (!form) {
        kukit.logWarning("No form found");
        return null;
    }
    return kukit.fo.getFormVar(form, name);
};

kukit.fo.getAllFormVarsFromCurrentForm = function(target) {
    // Just get one formvar, from the form that contains the target node
    var form = kukit.fo.getCurrentForm(target);
    if (!form) {
        kukit.logWarning("No form found");
        return {};
    }
    return kukit.fo.getAllFormVars(form);
};

kukit.fo.getAllFormVarsFromNamedForm = function(formname) {
    // Just get one formvar, from the named form 
    var form = document.forms[formname];
    if (!form) {
        kukit.logWarning("No form found");
        return {};
    }
    return kukit.fo.getAllFormVars(form);
};

/* With editors, there are two main points of handling:

   1. we need to load them after injected dynamically
   2. we need to prepare the form before we want to use the form variables

    Every editor has to register the field on their custody.
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
        throw 'Double registration of editor update on node.';
    }
    this.editors[hash] = editor;
    //kukit.logDebug('Registered '+node.name + ' hash=' + hash);
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

