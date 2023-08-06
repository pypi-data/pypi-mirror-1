(function($){
    
    function set_controls_position(container){
        var width = container.find('img').width();
        var left = (width/2) - 43;
        container.find('div.gallery-portlet-controls').css("left", left);
    }
    
    function get_image(link){
        var container = link.parent().parent().parent();
        var controls = container.find('div.gallery-portlet-controls');
        var next = controls.find('span.next a');
        var prev = controls.find('span.prev a');        
        var img = container.find('img');
        
         $.ajax({
             url : '@@get-image-for-gallery-portlet',
             data : link.attr('href').split('?')[1],
             type : 'GET',
             success : function(data, results){
                 eval("var json="+data);
                 img.fadeOut("slow", function(){
                     img.attr('src', json.src);
                     img.parent().attr('href', json['image-link']);
                     next.attr('href', next.attr('href').split('?')[0] + '?' + json['next-url']);
                     prev.attr('href', prev.attr('href').split('?')[0] + '?' + json['prev-url']);
                     set_controls_position(container);
                     img.fadeIn("slow");
                 });
             }
         });
    }
    
    var timeout_id = 0;
    
    function perform_play(portlet){
        portlet.find('span.next a').trigger('click');
        timeout_id = setTimeout(function(){perform_play(portlet);}, 5000);
    }   
     
    function play(portlet){
        portlet.addClass('timed');
        portlet.find('span.play-pause').addClass('timed');
        timeout_id = setTimeout(function(){perform_play(portlet);}, 5000);
    }
    
    function pause(portlet){
        portlet.removeClass('timed');
        portlet.find('span.play-pause').removeClass('timed');
        clearTimeout(timeout_id);
    }
    
    $(document).ready(function(){
        
        $('dl.portletGallery span.next a,dl.portletGallery span.prev a').click(function(){
            get_image($(this));
            return false;
        });
        
        $('dl.portletGallery span.play-pause').css({'display':'inline'});
        
        var portlets = $('dl.portletGallery');
        portlets.addClass('applied-portlet-gallery');
        
        portlets.each(function(){
            var portlet = $(this);
            set_controls_position(portlet);
            if(portlet.hasClass('timed')){
                play(portlet);
            }else{
                pause(portlet);
            }
        });
        
        $('dl.portletGallery span.play-pause a').click(function(){
            var portlet = $(this).parent().parent().parent();
            if(portlet.hasClass('timed')){
                pause(portlet);
            }else{
                play(portlet);
            }
            return false;
        });
        
        $('dl.portletGallery').hover(
            function(){
                var controls = $(this).find('div.gallery-portlet-controls');
                controls.fadeIn();
            },
            function(){
                var controls = $(this).find('div.gallery-portlet-controls');
                controls.fadeOut();
            }
        );
    });
})(jQuery);