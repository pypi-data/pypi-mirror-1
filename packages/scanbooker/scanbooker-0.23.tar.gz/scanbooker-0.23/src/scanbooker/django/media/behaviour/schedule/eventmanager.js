// EventManager
//
// EventManager is designed to look after the binding of events to elements
// identified by their CSS selectors. It can automatically bind events to all
// specified elements when you call EventManager#addAll, or you can add events
// individually (using EventManager#add) having previously specified them.
//
// It can also specify a binding which should be applied to all events, saving
// you from having to use global-scope variables and other such workarounds.
// In ScanBooker, the main Schedule instance is passed in as the default
// binding to all events.
//
// Lastly, we add an onEventsAdded event, so that elements can know when all
// their events have been added. This serves as a nice way of doing some
// set-up when your page loads without cramming all of it into your main
// domReady event.
//
// Example usage:
/*
myEvents = {
    'a.redlinks': {
        auto: true,
        onEventsAdded: function () {
            console.log("Redlink events added.")
        },
        click: function () {
            alert("You clicked on a redlink");
        },
        mouseover: function (event) {
            var elem = new Event(event).target;
            elem.addClass("hovered");
        }
    }
    'a.bluelinks': {
        click: function () {
            alert("You clicked on a bluelink");
        }
    }
}

evman = new EventManager(document, myEvents);

// 'this' will refer to 'document' in all events.

evman.addAll(); 

// At this point, "Redlink events added." will appear in the console, and the
// redlinks click and mouseover events will have been bound. 'auto' is not set
// for bluelinks, so a click on a bluelink won't do anything at this stage.

evman.add('a.bluelinks', $('container'));

// This will have added the bluelinks click event to all links with class
// bluelinks within #container.
*/

var EventManager = new Class({
    initialize: function (binding, events) {
        this.binding = binding;
        this.events = $H(events);
        this.added = [];
    },
    append: function (obj) {
        this.events.extend(obj);
    },
    add: function (selectorName, element, forceRebind) {
        element = element || document;
        var elements;
        this.events.each(function (eventsObj, selector) {
            // Bind all appropriate events, so if we have ".sel1 .sel2" in
            // this.events, calling with ".sel1" will include it.
            if (selectorName) {
                selector = selector.clean();
                selectorName = selectorName.clean();
                if (selector.substr(0, selectorName.length) !== selectorName) {
                    return;
                }
            }

            elements = element.getElements(selector);
            // Behave as expected if we are called with .selector,
            // <element class="selector" />.
            if ((elements.length === 0) &&
                (element !== document) &&
                (element.getParent()) &&
                (element.getParent().getElements(selectorName).contains(element))) {
                selector = selector.split(" ").slice(1).join(" ");
                if (selector.clean() === "") {
                    elements = [ element ];
                } else {
                    elements = element.getElements(selector);
                }
            }

            elements.each(function (elem) {
                if (this.added.contains(elem) && !forceRebind) {
                    // Don't bind twice.
                    console.warn("Not rebinding events to ", elem);
                    return;
                } else {
                    this.added.push(elem);
                    $each(eventsObj, function (fn, evName) {
                        // Don't try and bind a boolean value.
                        if (evName === 'auto') { return; }
                        elem.addEvent(evName, fn.bind(this.binding));
                    }, this);
                    elem.fireEvent('onEventsAdded', elem);
                }
            }, this);
        }, this);
    },
    addAll: function () {
        this.events.each(function (v, k) {
            var entry = this.events.get(k);
            if (entry && entry.auto) {
                this.add(k);
            }
        }, this);
    }
});

