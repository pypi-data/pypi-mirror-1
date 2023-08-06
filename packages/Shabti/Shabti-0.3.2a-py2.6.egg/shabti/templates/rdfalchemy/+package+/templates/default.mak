<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>

	<title>RDFLab</title>
	<style type="text/css">
    div { border:1px solid #aaf; width:97%; padding:1em; }
	</style>
</head>

<body>
    <h2>Store details</h2>
    <div>
    <pre>store type :: ${c.graph.store.__class__}</pre>
    <pre>context_aware :: ${c.graph.store.context_aware}</pre>
    <pre>contexts :: ${list(c.graph.store.contexts())}</pre>
    <pre>formula_aware :: ${c.graph.store.formula_aware}</pre>
    <pre>transaction_aware :: ${c.graph.store.transaction_aware}</pre>
    <pre>identifier :: ${c.graph.store.identifier}</pre>
    <pre>namespaces :: 
    %for ns in list(c.graph.store.namespaces()):
    ${ns}
    % endfor
    </pre>
    </div>
    <h2>Graph selection</h2>
    <div>
    <pre>>>> Company.get_by(symbol='IBM')</pre>
    <pre>${c.co}</pre>
    </div>
    <h2>Graph serialization to n3</h2>
    <div>
    <pre>${c.graph.serialize(format="n3")}</pre>
    </div>    
</body>
</html>
