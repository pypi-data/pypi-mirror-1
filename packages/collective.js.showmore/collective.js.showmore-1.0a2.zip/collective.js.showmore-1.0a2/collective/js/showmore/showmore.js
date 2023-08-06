(function($) {
 
    var LINK_TEXT = 'Show more...';
    var LINK_CLASS = 'showMoreLink';
    var HIDDEN_CLASS = 'showMoreHidden';
    var GRACE_COUNT = 1;
    
    $.fn.showMore = function(options) {
        // use custom link text if provided
        var text = options.link_text || LINK_TEXT;
        // use custom link class if provided
        var link_class = options.link_class || LINK_CLASS;
        // use custom hidden class if provided
        var hidden_class = options.hidden_class || HIDDEN_CLASS;
        // use custom grace count if provided
        var grace_count = options.grace_count || GRACE_COUNT;
        var nodesToHide = this.find(options.expression)
        // hide nodes only if there are enough to hide
        if (nodesToHide.length > grace_count) {
            // hide nodes
            nodesToHide.addClass(hidden_class).hide();
        }
        // create link
        var textNode = document.createTextNode(text);
        var clickHandler = function(e) {
                var parent = $(this).parent()
                // show hidden nodes
                parent.find('.' + hidden_class)
                      .removeClass(hidden_class)
                      .show();
                // remove link
                parent.find('.' + link_class)
                      .remove();
            };
        var link = $('<a />').addClass(link_class).append(textNode).
            css({cursor:'pointer'}).click(clickHandler);
        // add link only if there are hidden nodes
        var hasHiddenNodes = function(index) {
            var count = $(this).find('.' + hidden_class).length;
            return (count > 0);
        };
        this.filter(hasHiddenNodes).append(link);  
        return this
    };
})(jQuery);

