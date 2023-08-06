/*extern Element, $, $A, Sortables */
Element.extend({
    containsCoordinates: function (x, y) {
        var c = this.getCoordinates();
        return (x >= c.left &&
                y >= c.top &&
                x <= c.right &&
                y <= c.bottom);
    },
    // Add cross-browser rounded corners.
    addRoundedCorners: function (size) {
        if (window.ie && !window.ie6 && !window.ie7) {
            return false;
        } else {
            var cls, lim;
            var rctSpan = new Element('span', {'class': 'rtop'});
            var rcbSpan = new Element('span', {'class': 'rbottom'});
            if (size && size === 'small') {
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
        }
    },
    // Check length of input element against specified max, updating a display element
    // as necessary.
    checkLen: function (maxLen, displayElem) {
        displayElem = $(displayElem);

        if (!displayElem) { return false; }

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
    }
});

var SBSortables = Sortables.extend({
    initialize: function (schedule) {
        this.schedule = schedule;
        this.parent.apply(this, $A(arguments).slice(1));
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
                gap = c(-1).top - c(-2).bottom + (2 * d.slotMargin);
            } else {
                gap = c(-1).top - this.coordinates.top + d.slotMargin;
            }
            
            newTop = c(-1).top - this.coordinates.top - a.height + d.slotMargin;

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
                gap = c(2).top - c(1).bottom + (2 * d.slotMargin);
            } else {
                gap = this.coordinates.bottom - c(1).bottom - d.dayDatesHeight + d.slotMargin;
            } 
            
            newTop = c(1).bottom - this.coordinates.top - d.slotMargin;

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
                    this.limits.lower = c(-1).bottom - this.coordinates.top - d.slotMargin;
                } else {
                    this.limits.lower = d.scheduleBorder - d.slotMargin;
                }
                if (c(1)) {
                    this.limits.upper = c(1).top - this.coordinates.top - a.height + d.slotMargin
                } else {
                    this.limits.upper = this.coordinates.height - a.height - d.scheduleBorder + d.slotMargin - d.dayDatesHeight;
                }
            }
                
            newTop = now - this.coordinates.top - this.clickOffset;
            newTop = newTop.limit(this.limits.lower, this.limits.upper);
            this.active.setStyle('top', newTop);
        } 

        this.previous = now;
    }
});
// vim:ts=4:sw=4:sts=4:et:
