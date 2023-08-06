function get_all_nodes(elem)
{
    var ret = [elem];
    for(var node = elem.firstChild; node; node = node.nextSibling)
        ret = ret.concat(get_all_nodes(node))
    return ret;
}

/***
 * Dynamically add a form section
 **/
function add_section(ctrl, desc)
{
    // Find the id/name prefixes, and the next number in sequence
    var idprefix = ctrl.id.substring(0, ctrl.id.lastIndexOf('_grow-'));
    var nameprefix = ctrl.name.substring(0, ctrl.name.lastIndexOf('grow-'));

    var node = document.getElementById(idprefix + '_tbody').firstChild;
    while(node)
    {
        if(node.id && node.id.indexOf(idprefix + '_grow-') == 0)
            lastnode = node;
        node = node.nextSibling;
    }
    var number = parseInt(lastnode.id.substr(idprefix.length + 6)) + 1;

    // Clone the spare element; update id and name attributes
    var old_elem = document.getElementById(idprefix + '_spare');
    var elem = old_elem.cloneNode(true);
    var id_stemlen = idprefix.length + 6;
    var name_stemlen = nameprefix.length + (nameprefix ? 6 : 5);

    var new_name_prefix = nameprefix + (nameprefix ? '.' : '') + 'grow-' + number;
    var new_id_prefix = idprefix + '_grow-' + number;

    var x = get_all_nodes(elem)
    for(var i = 0; i < x.length; i++)
    {
        /* if(x[i].tagName && x[i].tagName == 'H2' && x[i].innerHTML.match(new RegExp("^" + desc)))
            x[i].innerHTML = desc + ' ' + (number+1); */
        if(x[i].name)
            x[i].name = new_name_prefix + x[i].name.substr(name_stemlen);
        if(x[i].id)
            x[i].id = new_id_prefix + x[i].id.substr(id_stemlen);
    }

    // Include new element in page
    document.getElementById(idprefix + '_tbody').insertBefore(elem, lastnode.nextSibling);

    // Remove onchange events from the last node, and make the delete button visible
    var x = get_all_nodes(lastnode)
    for(var i = 0; i < x.length; i++)
        x[i].onchange = null;
    var del = document.getElementById(idprefix + '_grow-' + (number-1) + '_del');
    if(del) del.style.display = '';
}

/**
 * Function to delete fields, with undo
 **/
var growing_undo_data = {};
function growing_del(ctrl)
{
    var idprefix = ctrl.id.substring(0, ctrl.id.lastIndexOf('_grow-'));
    var rowid = ctrl.id.substring(0, ctrl.id.lastIndexOf('_grow-')+7); // TBD: 7 needs tweaking
    if(!growing_undo_data[idprefix]) growing_undo_data[idprefix] = [];
    growing_undo_data[idprefix].push(rowid);
    document.getElementById(rowid).style.display = 'none';
    document.getElementById(idprefix + '_undo').style.display = '';
}
function growing_undo(ctrl)
{
    var idprefix = ctrl.id.substring(0, ctrl.id.length-5);
    document.getElementById(growing_undo_data[idprefix].pop()).style.display = '';
    if(!growing_undo_data[idprefix].length) ctrl.style.display = 'none';
}
