<%doc>
base.mako - Base template for the SMSShell application

Modify this template if you want to change the overall look of the application.

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title> ${c.title} POS </title>
<link href="${g.base_url}/smsshell.css" type="text/css" rel="stylesheet" />
<script src="${g.base_url}/js/areyousure.js" language="javascript" type="text/javascript"></script>
<script src="${g.base_url}/js/list.js" language="javascript" type="text/javascript"></script>
<script src="${g.base_url}/js/show_hide.js" language="javascript" type="text/javascript"></script>
<script src="${g.base_url}/js/text_counter.js" language="javascript" type="text/javascript"></script>
<script src="${g.base_url}/js/server.js" language="javascript" type="text/javascript"></script>
${h.javascript_include_tag(builtins=True)}
</head>

<body>

<div id="topBar">


</div>

<div id="sidebar">

<div id="title">
    <h1>
    <a href="${g.base_url}/">POS</a>
    </h1>
</div>

<div id="menu">

    <div>
    <ul>
        <li class="menuTop">Front End</li>
        <li><a href="${g.base_url}/sale_conv/" title="Convenience Store Sales">Convenience Store</a></li>
    </ul>
    </div>

    <div>
    <ul>
        <li class="menuTop">Master</li>
        <li><a href="${g.base_url}/branch/" title="List of Branches">Branch</a></li>
        <li><a href="${g.base_url}/classification/" title="List of Classifications">Classifications</a></li>
        <li><a href="${g.base_url}/item/" title="List of Items">Item</a></li>
    </ul>
    </div>

    <div>
    <ul>
        <li class="menuTop">Back End</li>
        <li><a href="${g.base_url}/transaction/" title="List of Transactions">Transactions</a></li>
        <li><a href="${g.base_url}/sale/" title="List of Sales">Sale</a></li>

        <li>Stocks</li>
        <li><a href="${g.base_url}/fuel/" title="List of Fuels">Fuel</a></li>
        <li><a href="${g.base_url}/service/" title="List of Services">Services</a></li>
        <li><a href="${g.base_url}/treats/" title="List of Treats">Treats</a></li>
        <li><a href="${g.base_url}/delivered/" title="List of Delivered Items">Deliveries</a></li>
        <li><a href="${g.base_url}/returns/" title="List of Item Returns">Returns</a></li>
        <li><a href="${g.base_url}/waste/" title="List of Wastage">Wastage</a></li>
        <li><a href="${g.base_url}/consumed/" title="List of Self-consumption">Self-Consumption</a></li>
        <li>Inventory</li>
        <li><a href="${g.base_url}/inventory/" title="Inventory">Inventory</a></li>

    </ul>
    </div>
</div>

</div>

<div id="main">
## ${self.body()}
## ${next.body()}
${self.body()}
</div>

<div id="footer">
<p>Copyright &copy; Emanuel Gardaya Calso</p>
</div>

</body>

</html>
