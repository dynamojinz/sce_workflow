odoo.define('sce_workflow.iframe_field', function (require) {
'use strict';

//var AbstractField = require('web.AbstractField');
var basicFields = require('web.basic_fields');
var fieldRegistry = require('web.field_registry');
//var field_utils = require('web.field_utils');

var FieldIframe = basicFields.InputField.extend({
    supportedFieldTypes: ['char'],

    /**
     * Render iframe open url in readonly mode.
     *
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        this.tagName = this.mode === 'readonly' ? 'iframe' : 'input';
    },


    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Returns the associated link.
     *
     * @override
     */
    getFocusableElement: function () {
        return this.mode === 'readonly' ? this.$el : this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * In readonly, the widget needs to be a iframe whose url in value.
     *
     * @override
     * @private
     */
    _renderReadonly: function () {
        this.$el.attr({
            src: this.value,
            width: this.attrs.width || "100%",
            height: this.attrs.height || "",
            scrolling: this.attrs.scrolling || "auto"
        });
    }
});

fieldRegistry.add('iframe', FieldIframe);

return {
    FieldIframe: FieldIframe,
};

});
