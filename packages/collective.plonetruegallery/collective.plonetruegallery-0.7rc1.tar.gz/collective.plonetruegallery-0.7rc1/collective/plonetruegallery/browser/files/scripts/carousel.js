

(function($) {

    $.fn.carousel = function(o) {
        return new $.carousel(this, o);
    };

    // Default configuration properties.
    var defaults = {
        show: true,
        images_to_show: 4,
        amount_to_rotate: 1
    };

    var buttonNextEvent = function(carousel){
        carousel.next();
    };
    
    var buttonPrevEvent = function(carousel){
        carousel.prev();
    };

    /**
     * The carousel object.
     *
     * @constructor
     * @name $.jcarousel
     * @param Object e The element to create the carousel for.
     * @param Hash o A set of key/value pairs to set as configuration properties.
     * @cat Plugins/jCarousel
     */
    $.carousel = function(e, o) {
        this.options    = $.extend({}, defaults, o || {});
        this.element = e;
        var self = this;
        
        var images = this.all_images();
        
        this.first = 0;
        
        for(var i = 0; i < this.options.images_to_show && i < images.length; i++){
            this.show_image(images[i]);
            this.last = i;
        }
        
        $(this.element).prepend("<div class='nextCarouselButton'></div>")
        $(this.element).find("div.nextCarouselButton").click(function(){buttonNextEvent(self)});
        $(this.element).append("<div class='prevCarouselButton'></div>")
        $(this.element).find("div.prevCarouselButton").click(function(){buttonPrevEvent(self)});
    };

    $.carousel.fn = $.carousel.prototype = {
        carousel: '0.1'
    };

    $.carousel.fn.extend = $.carousel.extend = $.extend;

    $.carousel.fn.extend({
        
        all_images: function(){
            return $(this.element).find("ul li");
        },
        
        all_active_images: function(){
            return $(this.element).find("ul li.active");
        },
        
        show_image: function(img){
            $(img).addClass("active").fadeIn(1000);
        },
        
        hide_image: function(img){
            $(img).removeClass("active").hide();
        },
        
        /**
         * Gets the size of the carousel.
         *
         * @name size
         * @type Integer
         * @cat Plugins/carousel
         */
        size: function() {
            return this.element.find('ul li').length;
        },


        /**
         * Adds an element for the given index to the list.
         *
         * @name add
         * @type jQuery
         * @param Number i The index of the element.
         * @param String imghtml The innerHTML of the element.
         * @cat Plugins/carousel
         */
        add: function(i, imghtml) {
            var all_images = this.all_images();
            var insert_after_image = all_images[i];
            
            $(insert_after_image).after("<li>" + imghtml + "</li>");
            
            return $(insert_after_image).next().find('img');
        },

        /**
         * Removes an element for the given index from the list.
         *
         * @name remove
         * @type undefined
         * @param Number i The index of the element.
         * @cat Plugins/jCarousel
         */
        remove: function(i) {
            $(this.all_images()[i]).remove()
        },

        /**
         * Moves the carousel forwards.
         *
         * @name next
         * @type undefined
         * @cat Plugins/jCarousel
         */
        next: function() {
            for(var i = 0; i < this.options.amount_to_rotate && !this.showing_last(); i++){
                var all_images = this.all_active_images();

                this.hide_image(all_images[0]);
                this.show_image($(all_images[all_images.length - 1]).next());
                
                this.first += 1;
                this.last += 1;
            }
        },

        /**
         * Moves the carousel backwards.
         *
         * @name prev
         * @type undefined
         * @cat Plugins/jCarousel
         */
        prev: function() {
            for(var i = 0; i < this.options.amount_to_rotate && !this.showing_first(); i++){
                var all_images = this.all_active_images();

                this.hide_image(all_images[all_images.length - 1]);
                this.show_image($(all_images[0]).prev());
                
                this.first -= 1;
                this.last -= 1;
            }
        },

        can_move_carousel: function(i){
            return ((i >= this.last && !this.showing_last()) || 
                        (i <= this.first && !this.showing_first()));
        },

        /**
         * Prepares the carousel and return the position for a certian index.
         *
         * @name pos
         * @type Number
         * @param Number i The index of the element to scoll to.
         * @cat Plugins/jCarousel
         */
        set_position: function(i) {
            while(this.can_move_carousel(i)){
                if(i > this.last){
                    this.next();
                }else{
                    this.prev();
                }
            }
        },
        
        showing_first: function(){
            var first_image = $(this.element).find("ul li:first");
            
            return first_image.hasClass('active');
        },
        showing_last: function(){
            var last_image = $(this.element).find("ul li:last");
            
            return last_image.hasClass("active");
        }
    });

    $.carousel.extend({
        /**
         * Gets/Sets the global default configuration properties.
         *
         * @name defaults
         * @descr Gets/Sets the global default configuration properties.
         * @type Hash
         * @param Hash d A set of key/value pairs to set as configuration properties.
         * @cat Plugins/jCarousel
         */
        defaults: function(d) {
            return $.extend(defaults, d || {});
        }
    });

})(jQuery);
