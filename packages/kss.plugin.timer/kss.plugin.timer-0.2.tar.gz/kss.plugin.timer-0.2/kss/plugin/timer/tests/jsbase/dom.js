var global = this;
global.domlib = new function domlib() {
    /* DOM helper functionality */
    var domlib = this;

    // the following three functions are HTML specific, but it seemed to make
    // sense to put them here anyway...
    domlib.hasClass = function hasClass(node, classname) {
        if (!node.className) {
            return false;
        };
        var classnames = node.className.split(' ');
        for (var i=0; i < classnames.length; i++) {
            if (classnames[i] == classname) {
                return true;
            };
        };
        return false;
    };

    domlib.addClass = function addClass(node, classname) {
        if (domlib.hasClass(node, classname)) {
            return;
        };
        if (!node.className) {
            node.className = classname;
        } else {
            node.className += ' ' + classname;
        };
    };

    domlib.removeClass = function removeClass(node, classname) {
        if (!node.className || !domlib.hasClass(node, classname)) {
            var msg = 'class ' + classname + ' not in ' + node.className;
            if (global.testing) {
                throw new testing.AssertionError(msg);
            } else {
                throw msg;
            };
            return;
        };
        var classnames = node.className.split(' ');
        var newclassnames = [];
        for (var i=0; i < classnames.length; i++) {
            var cn = classnames[i];
            if (cn != classname) {
                newclassnames.push(cn);
            };
        };
        node.className = newclassnames.join(' ');
    };

    domlib.toXML = function toXML(node, nonsingletonels, ns2p, p2ns) {
        /* convert a node to an XML string

            ns2prefix is used internally to determine when xmlns attrs should
            be generated
        */
        var displayxmlline = false;
        if (node.nodeType == 9) {
            node = node.documentElement;
            displayxmlline = true;
        };
        if (!ns2p && !p2ns) {
            ns2p = {};
            p2ns = {};
        } else if (!ns2p) {
            ns2p = {};
            for (var p in p2ns) {
                ns2p[p2ns[p]] = p;
            };
        } else if (!p2ns) {
            p2ns = {};
            for (var ns in ns2p) {
                p2ns[ns2p[ns]] = ns;
            };
        };
        // clone ns2p and p2ns for this layer
        var newns2p = {};
        for (var ns in ns2p) {
            newns2p[ns] = ns2p[ns];
        };
        ns2p = newns2p;

        var newp2ns = {};
        for (var p in p2ns) {
            newp2ns[p] = p2ns[p];
        };
        p2ns = newp2ns;
        var ret;
        if (node.nodeType == 3) {
            ret = string.entitize(node.nodeValue);
        } else if (node.nodeType == 8) {
            ret = '<!--' + node.nodeValue + '-->';
        } else if (node.nodeType == 1) {
            ret = _nodeToXML(node, nonsingletonels, ns2p, p2ns);
        };
        if (displayxmlline) {
            ret = '<?xml version="1.0" ?>\n' + ret;
        };
        return ret;
    };

    domlib.getTextFromNode = function(node) {
        var text = '';
        for (var i=0; i < node.childNodes.length; i++) {
            var child = node.childNodes[i];
            if (child.nodeType == 1) {
                text += ' ' + domlib.getTextFromNode(child);
            } else if (child.nodeType == 3) {
                text += ' ' + child.nodeValue;
            };
        };
        return string.strip(string.reduceWhitespace(text));
    };

    domlib.replaceContent = function replaceContent(node) {
        while (node.hasChildNodes()) {
            node.removeChild(node.lastChild);
        };
        for (var i=1; i < arguments.length; i++) {
            node.appendChild(arguments[i]);
        };
    };

    domlib.getElementsByClassName =
            function getElementsByClassName(node, className) {
        if (node.getElementsByClassName) {
            return node.getElementsByClassName(className);
        };
        var els = node.getElementsByTagName('*');
        var ret = [];
        for (var i=0; i < els.length; i++) {
            var el = els[i];
            var classes = el.className ? el.className.split(' ') : [];
            if (array.indexOf(classes, className) > -1) {
                ret.push(el);
            };
        };
        return ret;
    };

    var _nodeToXML = function _nodeToXML(node, nonsingletonels, ns2p, p2ns) {
        // the first thing we do is find out if we need new xmlns declarations
        var newns2p = {};
        // check the node's prefix/namespace
        for (var i=0; i < node.attributes.length; i++) {
            var attr = node.attributes[i];
            if (attr.namespaceURI != 'http://www.w3.org/2000/xmlns/') {
                continue;
            };
            var prefix;
            if (attr.localName == 'xmlns') {
                prefix = '__default__';
            } else {
                prefix = attr.localName;
            };
            if (!newns2p[attr.nodeValue] && !ns2p[attr.nodeValue]) {
                newns2p[attr.nodeValue] = prefix;
                ns2p[attr.nodeValue] = prefix;
                p2ns[prefix] = attr.nodeValue;
            };
        };

        // check what xmlns declarations are on the node
        var prefix = node.prefix || '__default__';
        var ns = node.namespaceURI;
        var newdefault = false;
        if (ns && p2ns[prefix] != ns && newns2p[prefix] != ns) {
            // new prefix
            newns2p[ns] = prefix;
            if (prefix == '__default__') {
                newdefault = true;
            };
        };

        // check the node attributes
        for (var i=0; i < node.attributes.length; i++) {
            var attr = node.attributes[i];
            if (attr.namespaceURI == 'http://www.w3.org/2000/xmlns/') {
                continue;
            };
            var aprefix = attr.prefix || '__default__';
            var ans = attr.namespaceURI;
            if (ans && p2ns[aprefix] != ans && !newns2p[ans]) {
                if (aprefix == '__default__') {
                    aprefix = _inventPrefix(p2ns, ans);
                };
                newns2p[ans] = aprefix;
            } else if (ns2p[ans] == '__default__') {
                newns2p[ans] = _inventPrefix(p2ns, ans);
            } else if (newns2p[ans] == '__default__') {
                // here we invent a new prefix for both the attr and the node,
                // note that we try to avoid this if possible
                delete newns2p[ans];
                newns2p[ans] = _inventPrefix(p2ns, ans);
            };
        };

        // now that we know the prefix/namespace mappings, we can start
        // serializing
        var xml = '<';
        var prefix = node.prefix || newns2p[node.namespaceURI] ||
                     ns2p[node.namespaceURI];
        if (prefix && prefix != '__default__') {
            xml += prefix + ':';
        };
        xml += node.localName;

        for (var i=0; i < node.attributes.length; i++) {
            var attr = node.attributes[i];
            var ans = attr.namespaceURI;
            var aname;
            if ((attr.nodeName == 'xmlns' &&
                        newns2p[attr.nodeValue] == '__default__') ||
                    (ans == 'http://www.w3.org/2000/xmlns/' &&
                        newns2p[attr.nodeValue] == attr.localName)) {
                delete newns2p[attr.nodeValue];
                aname = attr.nodeName;
            } else {
                aprefix = attr.prefix || newns2p[attr.namespaceURI] ||
                          ns2p[attr.namespaceURI];
                aname = '';
                if (aprefix && aprefix != '__default__'){
                    aname += aprefix + ':';
                };
                aname += attr.localName;
            };
            xml += ' ' + aname + '="' + string.entitize(attr.nodeValue) +
                   '"';
        };

        // now print new xmlns declarations
        for (var ns in newns2p) {
            if (ns == 'http://www.w3.org/2000/xmlns/' ||
                    ns == 'http://www.w3.org/XML/1998/namespace') {
                continue;
            };
            var tprefix = newns2p[ns];
            if (tprefix == '__default__') {
                xml += ' xmlns="';
            } else {
                xml += ' xmlns:' + tprefix + '="';
            };
            xml += string.entitize(ns) + '"';
            ns2p[ns] = tprefix;
            p2ns[tprefix] = ns;
        };
        if (!nonsingletonels) {
            nonsingletonels = {};
        };
        // XXX should this be node.localName instead?
        if (node.childNodes.length == 0 && !nonsingletonels[node.nodeName]) {
            xml += ' />';
        } else {
            xml += '>';
            for (var i=0; i < node.childNodes.length; i++) {
                xml += domlib.toXML(node.childNodes[i], nonsingletonels,
                                    ns2p, p2ns);
            };
            xml += '</';
            if (prefix && prefix != '__default__') {
                xml += prefix + ':';
            };
            xml += node.localName + '>';
        };
        return xml;
    };

    var _inventPrefix = function _inventPrefix(p2ns, ns) {
        // invent a new prefix; reserve it in the prefix space
        var aprefix = '';
        var j = 0;
        while (true) {
            aprefix = 'ns' + j;
            if (!p2ns[aprefix] || p2ns[aprefix] == ns) {
                break;
            };
            j++;
        };
        p2ns[aprefix] = ns;
        return aprefix;
    };
}();
