var AppendableFormFieldList = {

    li_count: null,

    li_template: null,

    removeItem: function(li_id) {
        li = document.getElementById(li_id);
        ol = li.parentNode;
        list_items = AppendableFormFieldList.getChildNodesByAttribute(ol, 'tagname', 'LI');
        AppendableFormFieldList.updateVars(ol);
        if (list_items.length == 1) {
            alert('Este item nao pode ser removido');
        }
        else {
            li.parentNode.removeChild(li);
        }
    },

    getChildNodesByAttribute: function(pnode, identifier, value) {
        new_nodes = new Array();
        nodes = pnode.childNodes;
        for (node_id in nodes) {
            node = nodes[node_id];
            if (identifier == 'tagname') {
                if (node && node.tagName == value) {
                    new_nodes.push(node);
                }
            }
            else if (node && node.getAttribute(identifier) == value) {
                new_nodes.push(node);
            }
        }
        return new_nodes;
    },

    updateVars: function(ol){
        list_items = AppendableFormFieldList.getChildNodesByAttribute(ol, 'tagname', 'LI');
        // Check Template
        if (AppendableFormFieldList.li_template == null) {
            AppendableFormFieldList['li_template'] = list_items[0];
        }
        // Check LI Count
        if (AppendableFormFieldList.li_count == null) {
            AppendableFormFieldList['li_count'] = list_items.length;
        }
    },

    addItem: function(ol_id) {
        ol = document.getElementById(ol_id);
        AppendableFormFieldList.updateVars(ol);
        list_items = AppendableFormFieldList.getChildNodesByAttribute(ol, 'tagname', 'LI');
        li_clone = AppendableFormFieldList.li_template.cloneNode(true);
        // Fix the labels.
        labels = li_clone.getElementsByTagName('LABEL');
        for (node_id in labels) {
            label = labels[node_id];
            // Why am I having to check for the node type?
            if (label.nodeType == 1) {
                var attributeValue = getNodeAttribute(label, 'for');
                label.setAttribute('for', attributeValue.replace(
                    '_0_', '_' + AppendableFormFieldList.li_count + '_'));
            }
        }
        // Fix the input values.
        inputs = li_clone.getElementsByTagName('INPUT');
        for (node_id in inputs) {
            input = inputs[node_id];
            if (input.nodeType == 1) {
                input.setAttribute('id', input.getAttribute('id').replace(
                    '_0_', '_' + AppendableFormFieldList.li_count + '_'));
                input.setAttribute('name', input.getAttribute('name').replace(
                    '-0', '-' + AppendableFormFieldList.li_count));
                input.value = '';
            }
        }
        // Fix select values.
        selects = li_clone.getElementsByTagName('SELECT');
        for (node_id in selects) {
            input = selects[node_id];
            if (input.nodeType == 1) {
                input.setAttribute('id', input.getAttribute('id').replace(
                    '_0_', '_' + AppendableFormFieldList.li_count + '_'));
                input.setAttribute('name', input.getAttribute('name').replace(
                    '-0', '-' + AppendableFormFieldList.li_count));
                input.value = '';
            }
        }
        // Fix textarea values.
        textareas = li_clone.getElementsByTagName('TEXTAREA');
        for (node_id in textareas) {
            input = textareas[node_id];
            if (input.nodeType == 1) {
                input.setAttribute('id', input.getAttribute('id').replace(
                    '_0_', '_' + AppendableFormFieldList.li_count + '_'));
                input.setAttribute('name', input.getAttribute('name').replace(
                    '-0', '-' + AppendableFormFieldList.li_count));
                input.value = '';
            }
        }
        li_clone.setAttribute('id', li_clone.getAttribute('id').replace(
            '_0', '_' + AppendableFormFieldList.li_count));
        // Add a remove link.
        ul = li_clone.getElementsByTagName('UL')[0];
        a_clones = ul.getElementsByTagName('A'); // Get all As
        // We just want the latest one since there can be other As inside
        // our formfield.
        a_clone = a_clones[a_clones.length - 1]; // It starts from zero...
        href_text = "javascript:AppendableFormFieldList.removeItem('" + 
            li_clone.getAttribute('ID') + "')";
        // a_clone.setAttribute('href', href_text);
        a_clone.href = href_text;
        log('A:', a_clone);
        // Finally.
        ol.appendChild(li_clone);
        // Focus
        // li_clone.getElementsByTagName('INPUT')[0].focus();
        AppendableFormFieldList['li_count'] = AppendableFormFieldList.li_count + 1;
    }
};

