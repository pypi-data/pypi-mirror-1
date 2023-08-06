<%doc>
edit.mako - Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<%inherit file="/edit_base.mako"/>

<%
%>

<%def name="show_children(entry)">
    %for child in c.children:
    <script language="javascript" type="text/javascript">
    <!--
    var column;
    var ${child}_cnt=0;
    var ${child}_price=Array();

    function add_child_${child}(child) {
        ${child}_cnt++;
        new Ajax.Updater('new-${child}-'+${child}_cnt, 'add_child?child=${child}&amp;cnt='+${child}_cnt, {asynchronous:true, evalScripts:true});
        //document.${child}-cnt.display: block;
        //return false;
    }

    function edit_child_${child}(cnt, id, p_id) {
        //${child}_cnt++;
        new Ajax.Updater('old-${child}-'+cnt, 'edit_child?c_id='+id+'&amp;p_id='+p_id+'&amp;child=${child}&amp;cnt='+cnt, {asynchronous:true, evalScripts:true});
        //document.${child}-cnt.display: block;
        //return false;
    }

    function show_change() {
        total_price = parseFloat(document.getElementById('total_price').value);
        total_tendered = parseFloat(document.getElementById('total_tendered').value);
        change = document.getElementById('change');
        //new Ajax.Updater('div-change', 'show_change?price=' + price +'&amp;tendered=' + tendered, {asynchronous:true, evalScripts:true});
        change.value = total_tendered - total_price;
    }

    function show_total() {
        total = 0;
        for (cnt=1; cnt<=trans_item_cnt; cnt++) {
            total = total + parseFloat(document.getElementById('price-'+cnt).value);
        }
        document.getElementById('total_price').value = total;
    }

    function show_price(cnt) {
        price = document.getElementById('price-'+cnt);
        item = document.getElementById('item-'+cnt);
        qty = document.getElementById('qty-'+cnt);
        new Ajax.Updater('div-price-'+cnt, 'show_price?cnt='+cnt+'&amp;item='+item.value+'&amp;qty='+qty.value, {asynchronous:false, evalScripts:true});
        //new Ajax.Updater('div-total_price', 'show_total_price', {asynchronous:true, evalScripts:true});
        //new Ajax.Updater('div-change', 'show_change?price='+total_price.value +'&amp;tendered='+total_tendered.value, {asynchronous:true, evalScripts:true});
        show_total();
        show_change();
    }

    //-->
    </script>
        ${self.show_child(child, entry)}
    %endfor
</%def>

<%def name="show_div_field(col)">
    <%
    if col == 'total_tendered':
        return show_div_field_tendered(col)
    %>
    <div id="div-${col}">
    ${self.show_field(col)}
    </div>
</%def>

<%def name="show_div_field_tendered(col)">
    <div id="div-${col}">
    <input id="${col}" name="${col}"
        onkeyup="show_change();"
        onkeydown="show_change();"
        />
    </div>
</%def>

