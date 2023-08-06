var ElementObject = new Class({
    initialize: function (type, options) {
        this.id = options.id;
        this.elem = new Element(type, options);
    },
    element: function () {
        this.elem = this.elem || $(this.id);
        return this.elem;
    },
    setElementFromDom: function () {
        this.elem = $(this.id);
    },
    getElement: function (selector) {
        return this.element().getElement(selector);
    },
    getElements: function (selector) {
        return this.element().getElements(selector);
    }
});

