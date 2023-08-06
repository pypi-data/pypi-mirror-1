/**
 * Hiding
 **/
var twd_mapping_store = {};
function twd_hiding_onchange(ctrl)
{
    if(ctrl.tagName == 'UL')
        return twd_hiding_list_onchange(ctrl);
    var cont = document.getElementById(ctrl.id+'.container');
    var visible = cont ? cont.style.display != 'none' : 1;
    var stem = ctrl.id.substr(0, ctrl.id.lastIndexOf('_')+1);
    var a, b;
    var mapping = twd_mapping_store[ctrl.id];
    var value = ctrl.type == 'checkbox' ? ctrl.checked : ctrl.value;
    for(a in mapping)
        for(b in mapping[a])
        {
            try {
                document.getElementById(stem+mapping[a][b]+'.container').style.display = (visible && (a == value)) ? '' : 'none';
            } catch(e) { alert('Missing control: ' + stem + mapping[a][b] + '.container'); }
            var x = document.getElementById(stem+mapping[a][b]);
            if(x && x.id && twd_mapping_store[x.id])
                twd_hiding_onchange(x);
        }
}

function twd_hiding_listitem_onchange(ctrl)
{
    twd_hiding_list_onchange(document.getElementById(
            ctrl.id.substr(0, ctrl.id.lastIndexOf('_'))));
}

function twd_hiding_list_onchange(ctrl)
{
    var cont = document.getElementById(ctrl.id+'.container');
    var visible = cont ? cont.style.display != 'none' : 1;
    var stem = ctrl.id.substr(0, ctrl.id.lastIndexOf('_')+1);
    var a, b;
    var mapping = twd_mapping_store[ctrl.id];
    // first, hide everything
    for(a in mapping)
        for(b in mapping[a])
        {
            document.getElementById(stem+mapping[a][b]+'.container').style.display = 'none';
            var x = document.getElementById(stem+mapping[a][b]);
            if(x && x.id && twd_mapping_store[x.id])
                twd_hiding_onchange(x);
        }
    // now, if we are visible, show everything that's selected
    if(visible)
        for(a in mapping)
            if(document.getElementById(ctrl.id+"_"+a).checked)
                for(b in mapping[a])
                {
                    document.getElementById(stem+mapping[a][b]+'.container').style.display = '';
                    var x = document.getElementById(stem+mapping[a][b]);
                    if(x && x.id && twd_mapping_store[x.id])
                        twd_hiding_onchange(x);
                }
}


/***
 * Growing
 **/
function twd_grow_add(ctrl, desc)
{
    // Find the id/name prefixes, and the next number in sequence
    if(ctrl.id.indexOf('_grow-') > -1)
    {
        // autogrow
        var autogrow = 1;
        var idprefix = ctrl.id.substring(0, ctrl.id.lastIndexOf('_grow-'));
        var nameprefix = ctrl.name.substring(0, ctrl.name.lastIndexOf('grow-'));
    }
    else
    {
        // button grow
        var autogrow = 0;
        var idprefix = ctrl.id.substring(0, ctrl.id.lastIndexOf('_add'));
        var nameprefix = ctrl.name.substring(0, ctrl.name.lastIndexOf('add'));
    }    
    var node = document.getElementById(idprefix + '_repeater').firstChild;
    while(node)
    {
        if(node.id && node.id.indexOf(idprefix + '_grow-') == 0)
            lastnode = node;
        node = node.nextSibling;
    }
    var number = parseInt(lastnode.id.substr(idprefix.length + 6)) + 1;

    // Clone the spare element; update id and name attributes; include in page
    var old_elem = document.getElementById(idprefix + '_spare');
    var elem = old_elem.cloneNode(true);
    var id_stemlen = idprefix.length + 6;
    var name_stemlen = nameprefix.length + 5;
    var new_name_prefix = nameprefix + 'grow-' + number;
    var new_id_prefix = idprefix + '_grow-' + number;
    var x = twd_get_all_nodes(elem)
    for(var i = 0; i < x.length; i++)
    {
        if(x[i].name) x[i].name = new_name_prefix + x[i].name.substr(name_stemlen);
        if(x[i].id) x[i].id = new_id_prefix + x[i].id.substr(id_stemlen);
    }
    document.getElementById(idprefix + '_repeater').insertBefore(elem, lastnode.nextSibling);

    // Remove onchange events from the last node, and make the delete button visible
    if(autogrow)
    {
        var x = twd_get_all_nodes(lastnode)
        for(var i = 0; i < x.length; i++)
            if(x[i].onchange)
                x[i].onchange = null;
        var del = document.getElementById(idprefix + '_grow-' + (number-1) + '_del');
        if(del) del.style.display = '';
    }
    
    // Clone any stored mappings for hiding fields
    for(id in twd_mapping_store)
        if(id.indexOf(idprefix + '_spare') == 0)
            twd_mapping_store[new_id_prefix + id.substr(id_stemlen)] = twd_mapping_store[id];
}

var twd_grow_undo_data = {};
function twd_grow_del(ctrl)
{
    var idprefix = ctrl.id.substring(0, ctrl.id.lastIndexOf('_grow-'));
    var rowid = ctrl.id.substring(0, ctrl.id.indexOf('_', idprefix.length+6));
    if(!twd_grow_undo_data[idprefix]) twd_grow_undo_data[idprefix] = [];
    twd_grow_undo_data[idprefix].push(rowid);
    document.getElementById(rowid).style.display = 'none';
    document.getElementById(idprefix + '_undo').style.display = '';
}

function twd_grow_undo(ctrl)
{
    var idprefix = ctrl.id.substring(0, ctrl.id.length-5);
    document.getElementById(twd_grow_undo_data[idprefix].pop()).style.display = '';
    if(!twd_grow_undo_data[idprefix].length) ctrl.style.display = 'none';
}

/**
 * Link container
 **/
function twd_link_onchange(ctrl)
{
    var visible = ctrl.style.display != 'none';
    var view = document.getElementById(ctrl.id.substr(0, ctrl.id.length-7) + '_view')
    view.style.display = visible && ctrl.value ? '' : 'none';
}

function twd_link_view(ctrl, link, popup_options)
{
    var value = document.getElementById(ctrl.id.substr(0, ctrl.id.length-5) + '_widget').value;
    window.open(link.replace(/\$/, value), '_blank', popup_options);
    return false;
}

/**
 * Utility functions
 **/
function twd_find_nodes(path)
{
    var ret = new Array();
    var seekl = path.indexOf('|') == -1 ? [path] : path.split('|');
    for(var i = 0; i < seekl.length; i++)
    {
        var nodes = document.getElementsByTagName(seekl[i]);
        for(var j = 0; j < nodes.length; j++)
            ret = ret.concat([nodes[j]]);
    }
    return ret;
}

function twd_is_hidden(node)
{
    while(node.tagName != 'BODY')
    {
        if(node.style.display == 'none')
            return 1;
        node = node.parentNode;
    }
    return 0;
}

function twd_blank_invisible()
{
    var x = twd_find_nodes('INPUT|SELECT|TEXTAREA');
    for(var i = 0; i < x.length; i++)
    {
        if(twd_is_hidden(x[i]))
            x[i].value = '';
    }
}

function twd_get_all_nodes(elem)
{
    var ret = [elem];
    for(var node = elem.firstChild; node; node = node.nextSibling)
        ret = ret.concat(twd_get_all_nodes(node))
    return ret;
}

function twd_suppress_enter(evt) {
    var evt = (evt) ? evt : ((event) ? event : null);
    var node = (evt.target) ? evt.target : ((evt.srcElement) ? evt.srcElement : null);
    if (evt.keyCode == 13)  {return node.type == 'textarea';}
}

function twd_find_node(node, suffix)
{
    var prefix = node.id.substr(0, node.id.lastIndexOf("_") + (suffix ? 1 : 0));
    return document.getElementById(prefix + suffix);
}

function twd_no_multi_submit(ctrl) {
    ctrl.disabled = 1;
    twd_find_node(ctrl, '').submit();
    return false;
}