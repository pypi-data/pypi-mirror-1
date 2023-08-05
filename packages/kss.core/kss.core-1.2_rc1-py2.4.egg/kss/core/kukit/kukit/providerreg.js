/*
* Copyright (c) 2005-2007
* Authors: KSS Project contributors
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

kukit.pr = {};

/*
*  class ParamProviderRegistry
* 
*  The parameter providers need to be registered here.
*/

kukit.pr.ParamProviderRegistry = function () {
    this.content = {};
};

kukit.pr.ParamProviderRegistry.prototype.register = function(name, func) {
    if (typeof(func) == 'undefined') {
        throw 'func argument is mandatory when registering a parameter provider (ParamProviderRegistry.register).';
    }
    ;;; if (this.content[name]) {
    ;;;    // Do not allow redefinition
    ;;;    kukit.logError('Error : parameter provider "' + name + '" already registered.');
    ;;;    return;
    ;;; }
    this.content[name] = func;
};

kukit.pr.ParamProviderRegistry.prototype.exists = function(name) {
    var entry = this.content[name];
    return (typeof(entry) != 'undefined');
};

kukit.pr.ParamProviderRegistry.prototype.get = function(name) {
    var func = this.content[name];
    if (! func) {
        // not found
        if (name == '') {
            // default provider for the strings
            return kukit.pr.IdentityPP;
         } else {
            ;;; kukit.E = 'Error : undefined parameter provider "' + name + '"';
            throw kukit.E;
        }
    }
    return func;
};

kukit.pprovidersGlobalRegistry = new kukit.pr.ParamProviderRegistry();

/*
* Register the core parameter providers
*
* A parameter provider is a class that needs to implement the 
* check and the eval methods.
* Check is executed at parsing time, eval is doing the real job
* of providing the requested parameter result.
* Check throws an exception if the parameters are not as expected.
* The parameters are coming in the input array "args". The current node is
* passed in "node". The output value should be returned.
*
* There is a third parameter that contains the default parameters
* dict (for input only). This is only used by the "pass()" parameter
* provider. The default parameters are used if an action is called
* programmatically but in this case the parameters to be propagated
* must be explicitely declared using the provider "pass()".
*
* The special key '' is held for the parameter provider that just returns
* the string itself. This is by default defined as the identity function, but
* can be overwritten to do something with the string value. The usage is that
* this provider expects a single parameter, the string.
*/

kukit.pr.IdentityPP = function() {};
kukit.pr.IdentityPP.prototype = {
    /*
    ;;; */
    check: function(args) {
        // check does not need to be used here actually.
        if (args.length != 1) {
            throw 'internal error, IdentityPP needs 1 argument';
        }
    },
    /*
    */
    eval: function(args, node) {
        return args[0];
    }
};
kukit.pprovidersGlobalRegistry.register('', kukit.pr.IdentityPP);

kukit.pr.FormVarPP = function() {};
kukit.pr.FormVarPP.prototype = {
    /*
    ;;; */
    check: function(args) {
        if (args.length != 2) {
            throw 'formVar method needs 2 arguments (formname, varname)';
        }
    },
    /*
    */
    eval: function(args, node) {
        return kukit.fo.getFormVar(new kukit.fo.NamedFormLocator(args[0]), args[1]);
    }
};
kukit.pprovidersGlobalRegistry.register('formVar', kukit.pr.FormVarPP);

kukit.pr.CurrentFormVarPP = function() {};
kukit.pr.CurrentFormVarPP.prototype = {
    /*
    ;;; */
    check: function(args) {
        if (args.length != 0 && args.length != 1) {
            throw 'currentFormVar method needs 0 or 1 argument (varname)';
        }
    },
    /*
    */
    eval: function(args, node) {
        if (args.length == 1) {
            return kukit.fo.getFormVar(new kukit.fo.CurrentFormLocator(node), args[0]);
        } else {
            // no form var name, just get the value of the node.
            return kukit.fo.getValueOfFormElement(node);
        }
    }
};
kukit.pprovidersGlobalRegistry.register('currentFormVar', kukit.pr.CurrentFormVarPP);

kukit.pr.CurrentFormVarFromKssAttrPP = function() {};
kukit.pr.CurrentFormVarFromKssAttrPP.prototype = {
    /*
    ;;; */
    check: function(args) {
        if (args.length != 1 && args.length != 2) {
            throw 'currentFormVarFromKssAttr method needs 1 or 2 argument (attrname, [recurseParents])';
        }
    },
    /*
    */
    eval: function(args, node) {
        var argname =  args[0];
        var recurseParents = false;
        if (args.length == 2) {
            ;;; kukit.E = '2nd attribute of currentFormVarForKssAttr must be a boolean';
            kukit.ut.evalBool(args[1], kukit.E);
            recurseParents = args[1];
        }
        var formvarname = kukit.dom.getRecursiveAttribute(node, argname, recurseParents, kukit.dom.getKssAttribute);
        return kukit.fo.getFormVar(new kukit.fo.CurrentFormLocator(node), formvarname);
    }
};
kukit.pprovidersGlobalRegistry.register('currentFormVarFromKssAttr', kukit.pr.CurrentFormVarFromKssAttrPP);


/* BBB. To be deprecated at 2007-08-15 */
kukit.pr.FormPP = function() {};
kukit.pr.FormPP.prototype = {
    /*
    ;;; */
    check: function(args) {
        if (args.length != 1) {
            throw 'form method needs 1 arguments (formname)';
        }
        kukit.logWarning('Deprecated the form(formname) parameter provider, use xxx-kssSubmitForm: form(formname) instead!');
    },
    /*
    */
    eval: function(args, node) {
        return kukit.fo.getAllFormVars(new kukit.fo.NamedFormLocator(args[0]), new kukit.ut.DictCollector());
    }
};
kukit.pprovidersGlobalRegistry.register('form', kukit.pr.FormPP);

/* BBB. To be deprecated at 2007-08-15 */
kukit.pr.CurrentFormPP = function() {};
kukit.pr.CurrentFormPP.prototype = {
    /*
    ;;; */
    check: function(args) {
        if (args.length != 0) {
            throw 'currentForm method needs no argument';
        }
        kukit.logWarning('Deprecated the currentForm() parameter provider, use xxx-kssSubmitForm: currentForm() instead!');
    },
    /*
    */
    eval: function(args, node) {
        return kukit.fo.getAllFormVars(new kukit.fo.CurrentFormLocator(node), new kukit.ut.DictCollector());
    }
};
kukit.pprovidersGlobalRegistry.register('currentForm', kukit.pr.CurrentFormPP);

kukit.pr.NodeAttrPP = function() {};
kukit.pr.NodeAttrPP.prototype = {
    /*
    ;;; */
    check: function(args) {
        if (args.length != 1 && args.length != 2) {
            throw 'nodeAttr method needs 1 or 2 argument (attrname, [recurseParents])';
        }
        if (args[0].toLowerCase() == 'style') {
            throw 'nodeAttr method does not accept "style" as attrname';
        }
        if (args[0].match(/[ ]/)) {
            throw 'attrname parameter in nodeAttr method cannot contain space.';
        }
    },
    /*
    */
    eval: function(args, node) {
        var argname = args[0];
        var recurseParents = false;
        if (args.length == 2) {
            recurseParents = args[1];
            ;;; kukit.E = '2nd attribute of nodeAttr must be a boolean';
            kukit.ut.evalBool(recurseParents, kukit.E);
        }
        return kukit.dom.getRecursiveAttribute(node, argname, recurseParents, kukit.dom.getAttribute);
    }
};
kukit.pprovidersGlobalRegistry.register('nodeAttr', kukit.pr.NodeAttrPP);

kukit.pr.KssAttrPP = function() {};
kukit.pr.KssAttrPP.prototype = {
    /*
    ;;; */
    check: function(args) {
        if (args.length != 1 && args.length != 2) {
            throw 'kssAttr method needs 1 or 2 argument (attrname, [recurseParents])';
        }
        if (args[0].match(/[ -]/)) {
            throw 'attrname parameter in kssAttr method cannot contain "-" or space.';
        }
    },
    /*
    */
    eval: function(args, node) {
        var argname =  args[0];
        var recurseParents = false;
        if (args.length == 2) {
            recurseParents = args[1];
            ;;; kukit.E = '2nd attribute of kssAttr must be a boolean';
            kukit.ut.evalBool(recurseParents, kukit.E);
        }
        return kukit.dom.getRecursiveAttribute(node, argname, recurseParents, kukit.dom.getKssAttribute);
    }
};
kukit.pprovidersGlobalRegistry.register('kssAttr', kukit.pr.KssAttrPP);

kukit.pr.NodeContentPP = function() {};
kukit.pr.NodeContentPP.prototype = {
    /*
    ;;; */
    check: function(args) {
        if (args.length != 0 && args.length != 1) {
            throw 'nodeContent method needs 0 or 1 argument (recursive)';
        }
    },
    /*
    */
    eval: function(args, node) {
        var recursive = false;
        if (args.length == 1) {
            recursive = args[0];
        }
        return kukit.dom.textContent(node, recursive);
    }
};
kukit.pprovidersGlobalRegistry.register('nodeContent', kukit.pr.NodeContentPP);

kukit.pr.StateVarPP = function() {};
kukit.pr.StateVarPP.prototype = {
    /*
    ;;; */
    check: function(args) {
        if (args.length != 1) {
            throw 'stateVar method needs 1 argument (varname)';
        }
    },
    /*
    */
    eval: function(args, node) {
        var key = args[0];
        var value = kukit.engine.statevars[key];
        if (typeof(value) == 'undefined') {
            // notfound arguments will get null
            ;;; kukit.E = 'Nonexistent statevar "'+ key +'"';
            throw kukit.E;
        }
        return value;
    }
};
kukit.pprovidersGlobalRegistry.register('stateVar', kukit.pr.StateVarPP);

kukit.pr.PassPP = function() {};
kukit.pr.PassPP.prototype = {
    /*
    ;;; */
    check: function(args) {
        if (args.length != 1) {
            throw 'pass method needs 1 argument (attrname)';
        }
    },
    /*
    */
    eval: function(args, node, defaultparms) {
        var key = args[0];
        var value = defaultparms[key];
        if (typeof(value) == 'undefined') {
            // notfound arguments will get null
            ;;; kukit.E = 'Nonexistent default parm "'+ key +'"';
            throw kukit.E;
        }
        return value;
    }
};
kukit.pprovidersGlobalRegistry.register('pass', kukit.pr.PassPP);

