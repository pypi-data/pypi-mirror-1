// create the top-level Z3C namespace if needed
if (typeof Z3C == "undefined" || !Z3C) {
    var Z3C = {};
}

// create a new namespace (under Z3C)
Z3C.namespace = function(name) {
    var ns = Z3C;
    var parts = name.split(".");
    if (parts[0] == "Z3C") {
        parts = parts.slice(1);
    }
    for (var i = 0; i < parts.length; i++) {
        var part = parts[i];
        ns[part] = ns[part] || {};
        ns = ns[part];
    }
    return ns;
};

(function() {
    Z3C.namespace('listjs');
        
    // return true if string starts with a prefix
    var startswith = function(s, prefix) {
        return (s.substring(0, prefix.length) == prefix);
    };

    // check whether a particular object is a number
    var isNumber = function(o) {
        return typeof o === 'number' && isFinite(o);
    };

    // change all numbers in a string with a dotted name to a new number
    // also renumber remove_X
    var renumber = function(s, nr) {
        var i;
        var fragment;
        var fragments = s.split('.');
        var result = [];
        for (i = 0; i < fragments.length; i++ ) {
            fragment = fragments[i];
            if (isNumber(parseInt(fragment))) {
                result[result.length] = nr.toString();
            } else if (startswith(fragment, 'remove_')) {
                result[result.length] = 'remove_' + nr.toString();
            } else {
                result[result.length] = fragment;
            }
        };
        return result.join('.');
    };

    
    // simplistic implementation that doesn't understand 
    // multiple classes per element
    var getElementsByClassName = function(class_name, root_el, tag) {
        tag = tag || '*';
        
        var result = [];
        var elements = root_el.getElementsByTagName(tag);
        
        for (var i = 0, len = elements.length; i < len; ++i) {
            if (elements[i].className) {
                result[result.length] = elements[i];
            }
        }
        return result;
    };

    // number all relevant attributes under el with nr
    var updateNumbers = function(el, nr, prefix) {
        // optimization - skip non-element nodes (ELEMENT_NODE 1)
        if (el.nodeType != 1) {
            return;
        }
        var i;
        var attributes = ['id', 'name', 'for'];
        for (i = 0; i < attributes.length; i++) {
            attr = el.getAttribute(attributes[i]);
            if (attr && startswith(attr, prefix)) {
                el.setAttribute(attributes[i], renumber(attr, nr));
            }
        }
        // recursion
        var node = el.firstChild;
        while (node) {
            updateNumbers(node, nr, prefix);
            node = node.nextSibling;
        }   
    };
    
    // update all numbers in el root
    var updateAllNumbers = function(prefix) {
        var table_el = document.getElementById(prefix + '.table');
        // update numbering in table
        var els = getElementsByClassName('list_item', table_el, 'tr');
        var i;
        for (i = 0; i < els.length; i++) {
            updateNumbers(els[i], i, 'form.');
        }
        // update count
        var count_el = document.getElementById(prefix + '.count');
        count_el.value = els.length;
    };

    // add a new repeating element to the list
    Z3C.listjs.add = function(prefix) {
        var table_el = document.getElementById(prefix + '.table');
        var template_el = document.getElementById(prefix + '.template');
        var template_text = template_el.value;
        var buttons_el = document.getElementById(prefix + '.buttons');

        // note that some DOM manipulation is needed as IE cannot
        // use innerHTML on tr directly. Instead we create the td
        // and put the widget contents in that.
        var new_tr = document.createElement('tr');
        new_tr.className = 'list_item';
        buttons_el.parentNode.insertBefore(new_tr, buttons_el);
        var td1 = document.createElement('td');
        var td2 = document.createElement('td');
        var td3 = document.createElement('td');
        new_tr.appendChild(td1);
        new_tr.appendChild(td2);
        new_tr.appendChild(td3);
        var cb = document.createElement('input');
        cb.className = 'editcheck';
        cb.type = 'checkbox';
        cb.name = prefix + '.remove_0';
        td1.appendChild(cb);
        td2.innerHTML = template_text;

        // up and down arrows
        var div_up = document.createElement('div');
        var div_down = document.createElement('div');
        var a_up = document.createElement('a');
        var a_down = document.createElement('a');
        a_up.className = 'up_button';
        a_down.className = 'down_button';
        a_up.onclick = function() {
            Z3C.listjs.up(prefix, this);
        };
        a_down.onclick = function() {
            Z3C.listjs.down(prefix, this);
        };
        td3.appendChild(div_up);
        td3.appendChild(div_down);
        div_up.appendChild(a_up);
        div_down.appendChild(a_down);
        
        updateAllNumbers(prefix);
    };
   
    // remove all selected repeating elements from the list
    Z3C.listjs.remove = function(prefix) {
        var table_el = document.getElementById(prefix + '.table');

        // find all elements that are checked
        var els = getElementsByClassName('editcheck', table_el, 'input');
        var i;
        var to_remove = [];
        for (i = 0; i < els.length; i++) {
            if (els[i].checked) {
                // remove the tr (two levels up from the input box)
                to_remove[to_remove.length] = els[i].parentNode.parentNode;
            }
        }
        // now actually remove them
        for (i = 0; i < to_remove.length; i++) {
            to_remove[i].parentNode.removeChild(to_remove[i]);
        }
        
        updateAllNumbers(prefix);
    };

    
    Z3C.listjs.up = function(prefix, el) {
        while (el.className != 'list_item') {
            el = el.parentNode;
        }
        var previous_el = el.previousSibling;
        while (previous_el != null && previous_el.className != 'list_item') {
            previous_el = previous_el.previousSibling;
        }
        // first list element, no move possible
        if (previous_el == null) {
            return;
        }
        previous_el.parentNode.insertBefore(el, previous_el);
        updateAllNumbers(prefix);
    };

    Z3C.listjs.down = function(prefix, el) {
        while (el.className != 'list_item') {
            el = el.parentNode;
        }
        var next_el = el.nextSibling;
        while (next_el != null && next_el.className != 'list_item') {
            next_el = next_el.nextSibling;
        }
        // last list element, no move possible
        if (next_el == null) {
            return;
        }
        next_el.parentNode.insertBefore(el, next_el.nextSibling);
        updateAllNumbers(prefix);
    };
    
})();
