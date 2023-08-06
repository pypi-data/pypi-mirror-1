;(function($) {

var defaults = {
    delay: 5,
    items: [],
    tag_class: 'galleriffic'
    
};
    
$.fn.gallerifficImageRotator = function(opzioni){
    // default configuration properties
    
    opzioni = $.extend(defaults, opzioni);
    tag_img = $(opzioni.tag_class);
    interval = opzioni.delay * 1000;
    image_index = 0;
    items = opzioni.items;
    Next = function(){
         if (items.length > 0){
             tag_img.attr('src', items[image_index % items.length ]);
             image_index++;
         }
    }
    Next();
    setInterval(Next, interval);
}

})(jQuery);