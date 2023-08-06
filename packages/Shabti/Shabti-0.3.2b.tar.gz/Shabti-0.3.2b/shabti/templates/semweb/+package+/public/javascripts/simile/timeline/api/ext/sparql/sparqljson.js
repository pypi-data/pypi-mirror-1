/*
 * Timeline function to load dat using SPARQL/JSON serialization format
 * http://www.w3.org/2001/sw/DataAccess/json-sparql/
 * by Alexandre Passant <alex@passant.org>
 */
Timeline.DefaultEventSource.prototype.loadSPARQLJSON = function(data, url) {
    var base = this._getBaseURL(url);
    var added = false;  
    if (data && data.results.bindings){

        var dateTimeFormat = ("dateTimeFormat" in data) ? data.dateTimeFormat : 'iso8601';
        var parseDateTimeFunction = this._events.getUnit().getParser(dateTimeFormat);
      
      	events = data.results.bindings;
        for (var i=0; i < events.length; i++){
            var event = events[i];
            var evt = new Timeline.DefaultEventSource.Event(
                parseDateTimeFunction((event.start) ? event.start.value : ''),
                parseDateTimeFunction((event.end) ? event.end.value : ''),
                parseDateTimeFunction((event.latestStart) ? event.latestStart.value: ''),
                parseDateTimeFunction((event.earliestEnd) ? event.earliestEnd.value: ''),
                (event.isDuration) ? event.isDuration.value : false,
                (event.title) ? event.title.value : '',
                (event.description) ? event.description.value : '',
                this._resolveRelativeURL((event.image) ? event.image.value : '', base),
                this._resolveRelativeURL((event.link) ? event.link.value : '', base),
                this._resolveRelativeURL((event.icon) ? event.icon.value : '', base),
                (event.color) ? event.color.value : '',
                (event.textColor) ? event.textColor.value : ''
            );
            evt._obj = event;
            evt.getProperty = function(name) {
                return this._obj[name];
            };

            this._events.add(evt);
            added = true;
        }
    }
   
    if (added) {
        for (var i = 0; i < this._listeners.length; i++) {
            this._listeners[i].onAddMany();
        }
    }
};
