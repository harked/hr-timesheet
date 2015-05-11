/**
 * Created by stclaus on 08.05.15.
 */
openerp.pet_store = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;

    var QWeb = instance.web.qweb;

    local.ColorInputWidget = instance.Widget.extend({
        template: "ColorInputWidget",
        events: {
            'change input': 'input_changed'
        },
        start: function() {
            this.input_changed();
            return this._super();
        },

        input_changed: function() {
            var color = [
                "#",
                this.$(".oe_color_red").val(),
                this.$(".oe_color_green").val(),
                this.$(".oe_color_blue").val(),
            ].join('');
            this.set("color", color);
        }
    });

    local.HomePage = instance.Widget.extend({
        template: "HomePage",
        start: function() {
            this.colorInput = new local.ColorInputWidget(this);
            this.colorInput.on("change:color", this, this.color_changed);
            return this.colorInput.appendTo(this.$el);
        },

        color_changed: function() {
            this.$(".oe_color_div").css("background-color", this.colorInput.get('color'));
        }
    });

    local.ProductWidget = instance.Widget.extend({
        template: "ProductWidget",
        init: function(parent, products, color) {
            this._super(parent);
            this.products = products;
            this.color = color;
        }
    });

    local.GreetingsWidget = instance.Widget.extend({
        init: function(parent, name) {
            this._super(parent);
            this.name = name;
        },

        start: function() {
            console.log(this.getParent());
            this.$el.append("<div>We are so happy to see you again in this menu!</div>");
        }
    });

    instance.web.client_actions.add(
        'petstore.homepage', 'instance.pet_store.HomePage'
    );
};