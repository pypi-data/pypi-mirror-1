// TODO: integrate this with the new MooTools Sortables class.

var SBSortables = new Class({
    Implements: [Events, Options],
    options: {
        handles: false,
        onStart: Class.empty,
        onComplete: Class.empty,
        ghost: true,
        snap: 3
    },
    initialize: function (schedule, list, options) {
        this.schedule = schedule;
        this.setOptions(options);
        this.list = $(list);
        this.elements = this.list.getChildren();
        this.handles = (this.options.handles) ? $$(this.options.handles) : this.elements;
        this.bound = {
            'start': []
        };
        for (var i = 0, l = this.handles.length; i < l; i++){
            this.bound.start[i] = this.start.bindWithEvent(this, this.elements[i]);
        }
        this.attach();
        if (this.options.initialize) this.options.initialize.call(this);
        this.bound.move = this.move.bindWithEvent(this);
        this.bound.end = this.end.bind(this);
    },

    attach: function(){
        this.handles.each(function(handle, i){
            handle.addEvent('mousedown', this.bound.start[i]);
        }, this);
    },

    detach: function(){
        this.handles.each(function(handle, i){
            handle.removeEvent('mousedown', this.bound.start[i]);
        }, this);
    },

    start: function(event, el){
        this.active = el;
        this.coordinates = this.list.getCoordinates();
        this.clickOffset = event.page.y - this.active.getPosition().y;
        this.origPrev = this.active.getPrevious();
        this.origNext = this.active.getNext();
        this.reset();
        document.addListener('mousemove', this.bound.move);
        document.addListener('mouseup', this.bound.end);
        this.fireEvent('onStart', el);
        event.stop();
    },
    end: function(){
        this.previous = null;
        document.removeListener('mousemove', this.bound.move);
        document.removeListener('mouseup', this.bound.end);
        if (this.options.ghost){
            document.removeListener('mousemove', this.bound.moveGhost);
            this.fireEvent('onDragComplete', [this.active, this.ghost]);
        }
        this.fireEvent('onComplete', this.active);
    },


    getElem: function (idx) {
        this.memo[idx] = this.memo[idx] || this.active.siblingAt(idx);
        return this.memo[idx];
    },
    getCoords: function (idx) {
        var elem = this.getElem(idx);
        return elem && elem.getCoordinates();
    },
    getElemWithShift: function (idx) {
        return this.getElem(idx + this.elemShift);
    },
    getCoordsWithShift: function (idx) {
        return this.getCoords(idx + this.elemShift);
    },
    reset: function () {
        this.limits = null;
        this.elemShift = 0;
        this.memo = {};
    },
    move: function (event) {
        event = new Event(event);
        var now = event.page.y;
        this.previous = this.previous || now;
        var up = (this.previous - now) > 0;

        var a = this.active.getCoordinates();
        var c = this.getCoordsWithShift.bind(this);
        var e = this.getElemWithShift.bind(this);
        var d = this.schedule.options.display;

        var gap, newTop;
        var uTip, dTip;

        if ((up && this.elemShift > 0) ||
            (!up && this.elemShift < 0)) {
            uTip = c(0) && (c(0).top + (c(0).height / 2));
            dTip = uTip;
        } else {
            uTip = c(-1) && (c(-1).top + (c(-1).height / 2));
            dTip = c(1) && (c(1).top + (c(1).height / 2));
        }

        if (up && uTip && now < uTip) {
            // We're moving upwards. Ditto above.
            if (c(-2)) {
                gap = c(-1).top - c(-2).bottom + (4 * d.slotMargin);
            } else {
                gap = c(-1).top - this.coordinates.top + (2*d.slotMargin);
            }

            newTop = c(-1).top - this.coordinates.top - a.height + (2*d.slotMargin);

            if (gap < a.height) {
                this.elemShift -= 1;
            } else {
                this.active.setStyle('top', newTop);
                this.active.injectBefore(e(-1));
                this.reset();
            }
        } else if (!up && dTip && now > dTip) {
            // We're moving downwards. Manually adjust top property of timeslot provided there's
            // enough room to put it there.
            if (c(2)) {
                gap = c(2).top - c(1).bottom + (4*d.slotMargin);
            } else {
                gap = this.coordinates.bottom - c(1).bottom - d.dayDatesHeight + (3*d.slotMargin);
            }

            newTop = c(1).bottom - this.coordinates.top - (2*d.slotMargin);

            if (gap < a.height) {
                this.elemShift += 1;
            } else {
                this.active.setStyle('top', newTop);
                this.active.injectAfter(e(1));
                this.reset();
            }
        } else {
            if (!this.limits) {
                this.limits = {};
                if (c(-1)) {
                    this.limits.lower = c(-1).bottom - this.coordinates.top - (2*d.slotMargin);
                } else {
                    this.limits.lower = d.scheduleBorder - d.slotMargin;
                }
                if (c(1)) {
                    this.limits.upper = c(1).top - this.coordinates.top - a.height + (2*d.slotMargin);
                } else {
                    this.limits.upper = this.coordinates.height - a.height - d.scheduleBorder + (2*d.slotMargin) - d.dayDatesHeight;
                }
            }

            newTop = now - this.coordinates.top - this.clickOffset;
            newTop = newTop.limit(this.limits.lower, this.limits.upper);
            this.active.setStyle('top', newTop);
        }

        this.previous = now;
    }
});