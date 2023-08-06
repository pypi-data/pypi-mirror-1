/*==================================================
 *  SPARQL Event Source for MIT Timeline
 *  by Morten Frederiksen
 *==================================================
 */

Timeline.DefaultEventSource.prototype.loadSPARQL = function(xml, url) {
    var base = this._getBaseURL(url);
    
/*    var dateTimeFormat = xml.documentElement.getAttribute("date-time-format");*/
    var dateTimeFormat = 'iso8601';
    var parseDateTimeFunction = this._events.getUnit().getParser(dateTimeFormat);

    if (xml == null)
        return null;
    var node = xml.documentElement.firstChild;
    while (node != null && (node.nodeType != 1 || node.nodeName != 'results'))
        node = node.nextSibling;
    if (node != null)
        node = node.firstChild;
    var added = false;
    while (node != null) {
        if (node.nodeType == 1) {
            var bindings = { };
            var binding = node.firstChild;
            while (binding != null) {
                if (binding.nodeType == 1 && binding.firstChild != null && binding.firstChild.nodeType == 1 && binding.firstChild.firstChild != null && binding.firstChild.firstChild.nodeType == 3)
                    bindings[binding.getAttribute('name')]=binding.firstChild.firstChild.nodeValue;
                binding = binding.nextSibling;
            }
            if (bindings["start"] == null && bindings["date"] != null)
                bindings["start"] = bindings["date"];
            var evt = new Timeline.DefaultEventSource.Event(
                parseDateTimeFunction(bindings["start"]),
                parseDateTimeFunction(bindings["end"]),
                parseDateTimeFunction(bindings["latestStart"]),
                parseDateTimeFunction(bindings["earliestEnd"]),
                bindings["isDuration"] != "true",
                bindings["title"],
                bindings["description"],
                this._resolveRelativeURL(bindings["image"], base),
                this._resolveRelativeURL(bindings["link"], base),
                this._resolveRelativeURL(bindings["icon"], base),
                bindings["color"],
                bindings["textColor"]
            );
            evt._bindings = bindings;
            evt.getProperty = function(name) {
                return this._bindings[name];
            };
            this._events.add(evt);
            added = true;
        }
        node = node.nextSibling;
    }

    if (added) {
        for (var i = 0; i < this._listeners.length; i++) {
            this._listeners[i].onAddMany();
        }
    }
};