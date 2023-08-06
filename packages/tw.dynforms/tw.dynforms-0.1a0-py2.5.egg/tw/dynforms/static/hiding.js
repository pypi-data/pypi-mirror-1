function hssf_change(thing, mapping)
{
    var cont = document.getElementById(thing.id+'.container');
    var visible = cont ? cont.style.display != 'none' : 1;
    var stem = thing.id.substr(0, thing.id.lastIndexOf('_')+1);
    var a, b;
    for(a in mapping)
        for(b in mapping[a])
        {
            try {
            document.getElementById(stem+mapping[a][b]+'.container').style.display = (visible && (a == thing.value)) ? '' : 'none';
            } catch(e) { alert('Missing control: ' + stem + mapping[a][b] + '.container'); }
            var x = document.getElementById(stem+mapping[a][b]);
            if(x) x = x.onchange;
            if(x) { x(); }
        }
}

function hcb_change(thing, mapping)
{
    var cont = document.getElementById(thing.id+'.container');
    var visible = cont ? cont.style.display != 'none' : 1;
    var stem = thing.id.substr(0, thing.id.lastIndexOf('_')+1);
    var a, b;
    for(a in mapping)
        for(b in mapping[a])
        {
            try {
            document.getElementById(stem+mapping[a][b]+'.container').style.display = (visible && (a == thing.checked)) ? '' : 'none';
            } catch(e) { alert('Missing control: ' + stem + mapping[a][b] + '.container'); }
            var x = document.getElementById(stem+mapping[a][b]).onchange;
            if(x) x();
        }
}

function sel_link_change(thing)
{
    var visible = thing.style.display != 'none';
    document.getElementById(thing.id + '.view').style.display = visible && thing.value ? '' : 'none';
}

function do_popup(thing, linkurl)
{
    var value = document.getElementById(thing.id.substr(0, thing.id.length-5)).value;
    window.open(linkurl.replace(/\$/, value));
}

function do_popup2(thing, linkurl)
{
    var value = document.getElementById(thing.id.substr(0, thing.id.length-5) + '.id').value;
    window.open(linkurl.replace(/\$/, value));
}


function find_nodes(path)
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

function is_hidden(node)
{
    while(node.tagName != 'BODY')
    {
        if(node.style.display == 'none')
            return 1;
        node = node.parentNode;
    }
    return 0;
}

function blank_invisible()
{
    var x = find_nodes('INPUT|SELECT|TEXTAREA');
    for(var i = 0; i < x.length; i++)
    {
        if(is_hidden(x[i]))
            x[i].value = '';
    }
}
