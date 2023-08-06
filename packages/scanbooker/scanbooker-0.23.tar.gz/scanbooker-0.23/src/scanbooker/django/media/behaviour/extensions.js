Element.implement({
    containsCoordinates: function (x, y) {
        var c = this.getCoordinates();
        return (x >= c.left &&
                y >= c.top &&
                x <= c.right &&
                y <= c.bottom);
    },
    // Add cross-browser rounded corners.
    addRoundedCorners: function (size) {
        var cls, lim;
        var rctSpan = new Element('span', {'class': 'rtop'});
        var rcbSpan = new Element('span', {'class': 'rbottom'});
        if (size === 'small') {
            cls = 'rs';
            lim = 2;
        } else {
            cls = 'r';
            lim = 4;
        }
        for (var ii = 0; ii < lim; ii += 1) {
            var x = new Element('span', {'class': cls + String(ii + 1)});
            var y = new Element('span', {'class': cls + String(lim - ii)});
            rctSpan.appendChild(x);
            rcbSpan.appendChild(y);
        }
        rctSpan.injectTop(this);
        rcbSpan.injectInside(this);
    },
    // Check length of input element against specified max, updating a display element
    // as necessary.
    checkLen: function (maxLen, displayElem) {
        displayElem = $(displayElem);

        if (!displayElem) { return }

        displayElem.setText(this.value.length);

        if (this.value.length > maxLen) {
            displayElem.addClass('error-text');
        } else {
            displayElem.removeClass('error-text');
        }
    },
    // Either grey or darken the function, setting text value as appropriate.
    toggleGreyed: function (greyedList) {
        var txt = greyedList[this.getProperty('id')];
        if (txt) {
            if (this.value === '') { this.value = txt; }
            if (this.hasClass('greyed')) {
                this.value = '';
                this.removeClass('greyed');
                this.addClass('darkened');
            } else {
                if (this.value === txt) {
                    this.removeClass('darkened');
                    this.addClass('greyed');
                }
            }
        }
    },
    // elem.getAncestor(3) == elem.getParent().getParent().getParent()
    getAncestor: function (n) {
        var elem = this;
        n = n || 1;
        for (n; n > 0; n -= 1) { elem = elem.getParent(); }
        return elem;
    },
    siblingAt: function (idx) {
        var sibling = (idx < 0) ? this.getPrevious : this.getNext;
        var elem = this;
        idx = ((idx < 0) ? idx * -1 : idx) || 0;
        for (idx; idx > 0; idx -= 1) { 
            elem = sibling.bind(elem)();
        }
        return elem;
    },
    formatContentsAsTimeStamp: function (formatStr) {
        var elem = this;
        var d = new Date();
        d.setTime(elem.getText().toInt() * 1000);
        elem.setText(d.strftime(formatStr));
    }
});

var SBDrag = new Class({
    Extends: Drag,
    start: function(event) {
        // TODO: remove 'orrible monkeypatch.
        //
        // This is because for some reason MooTools 1.2b2 provides no way that
        // I can find to stop this event propagating up the DOM. While fun to
        // watch, being unable to resize TimeSlots without moving them around
        // the page isn't actually all that useful...
        event.stop();
        arguments.callee.parent(event);
    }
});

