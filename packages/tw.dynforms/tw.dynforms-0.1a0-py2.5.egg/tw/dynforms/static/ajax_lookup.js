/**
 * JavaScript to support Ajax lookups
 **/
var popup_data  = null;
var popup_node  = null;
var popup_elem  = null;
var proc_req    = null;
var proc_node   = null;
var onfocus_val = null;

/**
 * Find a child node with a given suffix as its name
 **/
function find_node(node, suffix)
{
    for(var n = node.parentNode.firstChild; n; n = n.nextSibling)
        if(n.id && n.id.lastIndexOf(suffix, n.id.length - suffix.length)
                                                == n.id.length - suffix.length)
            return n;
}

function find_node2(node, suffix)
{
    for(var m = node.parentNode.parentNode.firstChild; m; m = m.nextSibling)
    {
        for(var n = m.firstChild; n; n = n.nextSibling)
                for(var o = n.firstChild; o; o = o.nextSibling)
                    if(o.id && o.id.lastIndexOf(suffix, o.id.length - suffix.length)
                                                == o.id.length - suffix.length)
                        return o;
    }
}


/**
 * When user clicks "view" popup a new window with contact details
 **/
function view_contact(self)
{
    var staffid = find_node(self, '.id').value;
    var url = "../pub/people?staffid=" + staffid;
    window.open(url, 'view_contact', 'toolbar=0,scrollbars=0,location=1,statusbar=1,menubar=0,resizable=1,width=500,height=400');
}

/**
 * When the entry box gets focus, clear all styles
 **/
function entry_onfocus(self)
{
    if(find_node(self, '.id').value)
        onfocus_val = self.value;
    else
        onfocus_val = 0;
    set_style(self, 0);
}

/**
 * When the entry box loses focus, validate using the server
 **/
function entry_onblur(self, evt, ajaxurl)
{
    if(self.value != '')
    {
        has_changed = 1;
    }
    if(onfocus_val && self.value == onfocus_val)
    {
        set_style(self, 1);
        onfocus_val = 0;
    }
    else
    {
        find_node(self, '.id').value = '';
        if(self.value != '')
            check_contact(self, ajaxurl);
    }
}

/**
 * Make the Ajax request to the server - asynchronous
 * If a request is already in progress, do nothing (but make entry box red)
 **/
function check_contact(node, ajaxurl)
{
    if(proc_req)
    {
        set_style(node, 2);
        alert('A search is already in progress; please let it complete before making another.');
        return;
    }
    set_style(node, 3);
    proc_node = node;
    proc_req = newXMLHttpRequest();
    proc_req.onreadystatechange = process_response;
    proc_req.open("POST", ajaxurl, true);
    proc_req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
    proc_req.send("search=" + escape(find_node(node, '.entry').value));
}

/**
 * This function is invoked when the response is ready
 **/
function process_response()
{
    if(proc_req.readyState != 4) return;
    if(proc_req.status != 200)
    {
        set_style(proc_node, 2);
        proc_req = null;
        proc_node = null;
        alert('Server error processing request');
        return;
    }
    var data = eval('x=' + proc_req.responseText);

    if(data['status'] != 'Successful')
    {
        set_style(proc_node, 2);
        alert(data['status']);
    }
    else if(data['data'].length == 0)
        set_style(proc_node, 2);
    else if(data['data'].length == 1)
    {
        var data = data['data'][0];
        find_node(proc_node, '.entry').value = data['value'];
        find_node(proc_node, '.id').value = data['id'];
        set_style(proc_node, 1);
    }
    else if(popup_data)
    {
        set_style(proc_node, 2);
        alert('Please select a contact from the open popup before performing another search.');
    }
    else
    {
        popup_node = proc_node;
        popup_data = data;
        raise_popup();
    }

    proc_req = null;
    proc_node = null;
}

/**
 * Set the style of a contact row
 **/
function set_style(node, num)
{
    var entry = find_node(node, '.entry');
    var view  = find_node(node, '.link');

    if(num == 0) /* editing */
    {
        entry.disabled = false;
        entry.style.backgroundColor = 'white';
        entry.style.textDecoration = '';
        view.style.display = 'none';
    }
    if(num == 1) /* matched */
    {
        entry.disabled = false;
        entry.style.backgroundColor = 'white';
        entry.style.textDecoration = 'underline';
        view.style.display = 'inline';
    }
    if(num == 2) /* problem */
    {
        entry.disabled = false;
        entry.style.backgroundColor = 'red';
        entry.style.textDecoration = '';
        view.style.display = 'none';
    }
    if(num == 3) /* working */
    {
        entry.disabled = true;
        view.style.display = 'none';
    }
}

/**
 * Raise the popup layer
 **/
function raise_popup()
{
    var html = "<table class='padded popup' onclick='event.cancelBubble = true'>";
    for(var i = 0; i < popup_data['data'].length; i++)
    {
        var d = popup_data['data'][i];
        html += "<tr><td><a href='pick' onclick='pick_contact(" + i + "); return false;'>"
                 +    d['id'] + "</a></td><td>" + d['value'] + "</td></tr>";
    }
    html += "<tr><td><a href='cancel' onclick='cancel_popup(); return false;'>Cancel</a></td></tr></table>";

    popup_elem = document.createElement('TR');
    popup_elem.appendChild(document.createElement('TD'));
    popup_elem.firstChild.colSpan = 5;
    popup_elem.firstChild.innerHTML = html;
    var tr_node = popup_node.parentNode.parentNode.parentNode;
    tr_node.parentNode.insertBefore(popup_elem, tr_node.nextSibling);
}

/**
 * When a user clicks a contact to select it, do the necessary.
 **/
function pick_contact(i)
{
    var data = popup_data['data'][i];
    find_node(popup_node, '.entry').value = data['value'];
    find_node(popup_node, '.id').value = data['id'];
    set_style(popup_node, 1);
    hide_popup();
}

/**
 * Hide the popup layer
 **/
function hide_popup()
{
    popup_elem.parentNode.removeChild(popup_elem);
    popup_data = null;
    popup_node = null;
    popup_elem = null;
}

/**
 * When the document is clicked, if the popup layer is open, hide it.
 * Also, set the current contact entry box to "problem".
 **/
function cancel_popup()
{
    set_style(popup_node, 2);
    hide_popup();
}

/**
 * Create an XMLHttpRequest object portably (both IE and Mozilla)
 **/
function newXMLHttpRequest()
{
    if(window.ActiveXObject)
        return new ActiveXObject("Microsoft.XMLHTTP");
    return new XMLHttpRequest();
}
