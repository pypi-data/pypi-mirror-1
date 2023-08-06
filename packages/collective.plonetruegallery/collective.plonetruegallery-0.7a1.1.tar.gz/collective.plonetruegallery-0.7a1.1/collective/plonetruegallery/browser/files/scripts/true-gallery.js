var getKssAttr = function(element, key){
    element = jq(element);
    
    if(element.size() == 0 || element[0].className == undefined){
        return "";
    }
    
    var classes = element[0].className.split(' ');
    
    var startsplit = 'kssattr-'.length;
    var endsplit = startsplit + key.length;
    
    for(var i = 0; i < classes.length; i++){
        if(classes[i].substring(0, startsplit) == 'kssattr-'){
            if(classes[i].substring(startsplit, endsplit) == key){
                return classes[i].substring(endsplit+1, classes[i].length);
            }
        }
    }
};

TrueGallery = function(element, options){
    var defaults ={
        carouselOptions: {},
        hideSpeed: 0,
        showSpeed: 0,
        hideType: 'fade',
        showType: 'fade',
        showCarousel: true,
        timed: true,
        delay: 2000,
        showInfo: true
    };
    
    jq = jQuery.noConflict();
    tg = this;
    
    tg.selectors = {
        imageContainerSelector: "div#plone-true-gallery div.view div.image",
        firstImageContainer: "div#plone-true-gallery div.view div.image:first",
        imageSelector: "div#plone-true-gallery div.view div.image img",
        placeImage: "div#plone-true-gallery div.view div.place-image img",
        imagesContainerSelector: 'div#plone-true-gallery div.view',
        selectedImageSelector: "div#plone-true-gallery div.view div.selected img",
        selectedImageContainerSelector: "div#plone-true-gallery div.view div.selected",
        descriptionSelector: "div#plone-true-gallery div.info p",
        titleSelector: "div#plone-true-gallery div.info h2",
        linkSelector: "div#plone-true-gallery div.info a",
        carouselSelector: "div#plone-true-gallery ul.carousel",//before it is generated
        carouselSelectorAfterGeneration: "div#plone-true-gallery div div.jcarousel-container",
        carouselClipSelector: 'div.jcarousel-clip',
        carouselListSelector: 'div.jcarousel-clip ul.carousel',
        carouselItemSelector: 'div.jcarousel-clip ul.carousel li.jcarousel-item',
        carouselImgSelector: 'div.jcarousel-clip ul.carousel li.jcarousel-item img',
        carouselContainer: 'div#plone-true-gallery div div.jcarousel-container',
        media: {
            next: 'div#plone-true-gallery div.view div#media-guide ul li.next',
            prev: 'div#plone-true-gallery div.view div#media-guide ul li.prev',
            first: 'div#plone-true-gallery div.view div#media-guide ul li.first',
            last: 'div#plone-true-gallery div.view div#media-guide ul li.last',
            pause: 'div#plone-true-gallery div.view div#media-guide ul li.pause',
            play: 'div#plone-true-gallery div.view div#media-guide ul li.play'
        },
        loadMoreImagesButtonSelector: 'div#plone-true-gallery input#loadMoreImages',
        infoPaneSelector: 'div#plone-true-gallery div.info',
        galleryViewSelector: 'div#plone-true-gallery div.view',
        mediaGuideSelector: 'div#plone-true-gallery div.view div#media-guide',
        mediaButtonSelector: 'div#plone-true-gallery div.view div#media-guide ul li',
        trueGallery: 'div#plone-true-gallery'
    };
    
    //specifies when loading of more images will be triggered
    tg.preloadImageOffset = 5;
    
    //when done loading images...
    tg.doneLoading = false;
    
    //set to know when toggling an image
    tg.toggling = false;
    
    //used for timer
    tg.activelyTimed = false;
    
    tg.autoLoadingEnabled = true;
    
    tg.requestInProgress = false;
    
    /*
     * Each effect must have a hide and show function
     * each function must accept the true gallery instance, image to perform on, and the callback method
     *
    */
    tg.effects = {
        fade: {
            hide: function(image, nextImage, cb){
                jq(tg.selectors.galleryViewSelector).height(nextImage.height());
                return image.fadeOut(tg.options.hideSpeed, cb);
            },
            show: function(image, previousImage, cb){
                return image.fadeIn(tg.options.showSpeed, cb);
            }
        },
        slide: {
            hide: function(image, nextImage, cb){
                jq(tg.selectors.galleryViewSelector).height(nextImage.height());
                return image.slideUp(tg.options.hideSpeed, cb);
            },
            show: function(image, previousImage, cb){
                return image.slideDown(tg.options.showSpeed, cb);
            }
        },
        show: {
            hide: function(image, nextImage, cb){
                jq(tg.selectors.galleryViewSelector).height(nextImage.height());
                return image.hide(tg.options.hideSpeed, cb);
            },
            show: function(image, previousImage, cb){
                return image.fadeIn(tg.options.showSpeed, cb);
            }
        },
        animate: {
            hide: function(image, nextImage, cb){
                jq(tg.selectors.galleryViewSelector).height(nextImage.height());
                return image.animate({
                    width: '0px',
                    height: '0px',
                    opacity: 0.0
                }, tg.options.hideSpeed, cb);
            },
            show: function(image, previousImage, cb){
                var prevWidth = image.width();
                var prevHeight = image.height();
                image.width(0);
                image.height(0);
                image.show();
                image.css('opacity', 0.0);
                return image.animate({
                    width: prevWidth + 'px',
                    height: prevHeight + 'px',
                    opacity: 1.0
                }, tg.options.showSpeed, cb);
            }
        }
    };
    
    /**
     * constructor of gallery
     *
     * @name reload
     * @param Element element The gallery element to create this on
     * @param JSON o options that the gallery will use
     * @type void
     */
    tg.initialize = function(element, o){
        tg.options = jq.extend({}, defaults, o || {});
        tg.imageContainer = jq(tg.selectors.galleryViewSelector);
        
        tg.createCarousel();

        if(!tg.options.showInfo){
            jq(tg.selectors.infoPaneSelector).hide();
        }

        tg.setupButtonClickEvents();
        tg.setupButtonHoverEvents();
        tg.setupImgHoverEvent();
        tg.setupImgClickEvent();
        
        tg.setupGalleryHoverEvent();
        
        tg.selectFirstImage();
        
        tg.setupAutomaticLoadingOfImages();
        tg.setupTimer();
    };
    
    tg.selectFirstImage = function(){
        var selectedDiv = jq(tg.selectors.firstImageContainer).addClass('selected');

        tg.setInfo();
    }
    
    tg.setInfo = function(){
        var images = jq(tg.selectors.imageContainerSelector);
        var selectedIndex = 1;
        for(var i = 0; i < images.size(); i++){
            var img = jq(images[i]);
            if(img.hasClass('selected')){
                selectedIndex = i;
                containerImage = img;
                break;
            }
        }
        
        var containerImage = jq(tg.selectors.selectedImageContainerSelector);
        
        var numberOfImages = getKssAttr(jq('div#plone-true-gallery')[0], 'numberOfImages');
        
        jq(tg.selectors.titleSelector).html(containerImage.find('h2').html() + " (" + (selectedIndex+1) + "/" + numberOfImages + ")");
        jq(tg.selectors.descriptionSelector).html(containerImage.find('p').html());
        jq(tg.selectors.linkSelector).attr('href', getKssAttr(containerImage[0], 'link'));
    };
    
    tg.setupButtonHoverEvents = function(){
        jq(tg.selectors.mediaButtonSelector).hover(
            function(){ jq(this).addClass('hoverThumbnail');},
            function(){ jq(this).removeClass('hoverThumbnail');}
        );
    };
    
    tg.setupButtonClickEvents = function(){
        
        jq(tg.selectors.media.first).click(tg.getFirstImage);
        jq(tg.selectors.media.prev).click(tg.getPrevImage);
        jq(tg.selectors.media.pause).click(tg.pause);
        jq(tg.selectors.media.play).click(tg.play);
        jq(tg.selectors.media.next).click(tg.getNextImage);
        jq(tg.selectors.media.last).click(tg.getLastImage);
    };
    
    tg.setupAutomaticLoadingOfImages = function(){
        
        if(tg.autoLoadingEnabled){
            jq('div#plone-true-gallery').everyTime('3s', 'load images', function(){
                if(!tg.doneLoading){
                    tg.addImages();
                }else{
                    jq('div#plone-true-gallery').stopTime('load images');
                }
            });
        }
    }
    
    tg.setupTimer = function(){
        if(tg.options.timed){
            jq(tg.selectors.media.play).hide();
            jq(tg.selectors.media.pause).show();
            jq(tg.selectors.media.pause).css('display', 'block'); //safari hiccups?
            tg.startTimer();
        }else{
            jq(tg.selectors.media.play).show();
            jq(tg.selectors.media.play).css('display', 'block'); //safari hiccups?
            jq(tg.selectors.media.pause).hide();
        }
    };
    
    tg.stopTimer = function(){
        if(tg.activelyTimed){
            tg.activelyTimed = false;
            jq(tg.selectors.media.play).stopTime('next image');
        }
    };
    
    tg.startTimer = function(){
        if(!tg.activelyTimed){
            tg.activelyTimed = true;
            jq(tg.selectors.media.play).everyTime(tg.options.delay, 'next image', tg.getNextImage);
        }
    };
    
    tg.pause = function(){
        tg.stopTimer();
        jq(tg.selectors.media.pause).hide();
        jq(tg.selectors.media.play).show();
    };
    
    tg.play = function(){
        tg.startTimer();
        jq(tg.selectors.media.play).hide();
        jq(tg.selectors.media.pause).show();
    };
    
    tg.triggerLoadMoreImages = function(){
        if(tg.jcar.size() < (tg.jcar.last + tg.preloadImageOffset) && !tg.doneLoading){
            tg.addImages();
        }
    };
    
    tg.createCarousel = function(){
        tg.options.carouselOptions.initCallback = function(carousel, state){
            tg.jcar = carousel;
        };
        jq(tg.selectors.carouselSelector).show();
        jq(tg.selectors.carouselSelector).css('display', 'block'); //safari hiccups?
        jq(tg.selectors.carouselSelector).jcarousel(tg.options.carouselOptions);
        
        if(!tg.options.showCarousel){
            jq(this.selectors.carouselContainer).parent().hide();
        }
    };
    
    tg.getNextImage = function(){
        var currentImage = jq(tg.selectors.selectedImageContainerSelector);
        var nextImage = currentImage.next('div.image');

        if(nextImage.length > 0){
            tg.toggleImage(currentImage, nextImage);
        }else{
            tg.toggleImage(currentImage, jq(tg.selectors.imageContainerSelector + ':first'));
        }
        tg.triggerLoadMoreImages();
    };
    
    tg.getFirstImage = function(){
        var currentImage = jq(tg.selectors.selectedImageContainerSelector);
        tg.toggleImage(currentImage, jq(tg.selectors.imageContainerSelector + ':first'));
    };
    
    tg.getPrevImage = function(){
        var currentImage = jq(tg.selectors.selectedImageContainerSelector);
        var prevImage = currentImage.prev('div.image');
        
        if(prevImage.length > 0){
            tg.toggleImage(currentImage, prevImage);
        }else{
            //get last image
            tg.toggleImage(currentImage, jq(tg.selectors.imageContainerSelector + ':last'));
        }
    };
    
    tg.getLastImage = function(){
        var currentImage = jq(tg.selectors.selectedImageContainerSelector);
        var prevImage = currentImage.prev('div:last');

        tg.toggleImage(currentImage, jq(tg.selectors.imageContainerSelector + ':last'));
    };
    
    tg.hide = function(image, nextImage, cb){
        return tg.effects[tg.options.hideType].hide(image, nextImage, cb);
    };
    
    tg.show = function(image, previousImage, cb){
        return tg.effects[tg.options.showType].show(image, previousImage, cb);
    };
    
    tg.getCarouselPos = function(image){
        image = typeof(image.length) == "undefined" ? image : image[0];
        var index = parseInt(getKssAttr(image, 'index')) + 1;

        return index - Math.round((tg.jcar.last - tg.jcar.first)/2);
    };
    
    tg.setNewCarouselPosition = function(pos){
        tg.jcar.scroll(pos, true);
        tg.triggerLoadMoreImages();
    };

    /*
     * setImageContainerHeight
     * used to fix some opera bugs where the height the 
     * gallery would just be lost when toggling images
     * very hackish, but I couldn't figure out any
     * other way
    */
    tg.setImageContainerHeight = function(){
        var container = jq(tg.selectors.trueGallery);
            
        var height = 0;
        var children = container.children();
        
        for(var i = 0; i < children.size(); i++){
            height += jq(children[i]).outerHeight();
        }
            
        container.height(height);
    }

    /*
     * toggleImage
     * switch bewtween two images
     * both images it takes should be in the image container div
     *
    */
    tg.toggleImage = function(currentImage, newImage){
        currentImage = typeof(currentImage.length) != "undefined" ? currentImage : jq(currentImage);
        newImage = typeof(newImage.length) != "undefined" ? newImage : jq(newImage);
        
        if(newImage[0] != currentImage[0] && !tg.toggling){
            tg.toggling = true;
            
            tg.hide(currentImage.find('img'), newImage.find('img'), function(){
                currentImage.removeClass('selected');                 
                
                tg.show(newImage.find('img'), currentImage.find('img'), function(){
                    newImage.addClass('selected');
                    tg.setNewCarouselPosition(tg.getCarouselPos(newImage));
                    tg.setInfo();
                    tg.setImageContainerHeight() //This is to fix dynamic sizing with opera and sometimes other browsers.
                    tg.toggling = false;
                });
            });
        }
    };
    
    tg.imgClickEvent = function(){
        var index = getKssAttr(this, 'index');

	    var newImage = jq(tg.selectors.imageContainerSelector)[parseInt(index)];
	    var currentImage = jq(tg.selectors.selectedImageContainerSelector);

	    tg.toggleImage(currentImage, newImage);
    };
    
    tg.imgHoverOn = function(){ jq(this).addClass('hoverThumbnail'); };
    
    tg.imgHoverOut = function(){ jq(this).removeClass('hoverThumbnail'); };
    
    tg.setupImgHoverEvent = function(){
        return jq(tg.selectors.carouselImgSelector).hover(tg.imgHoverOn, tg.imgHoverOut);
    };
    
    tg.setupImgClickEvent = function(){
        return jq(tg.selectors.carouselImgSelector).click(tg.imgClickEvent);
    };
    
    tg.addImgEvents = function(images){
        images.click(tg.imgClickEvent);
        images.hover(tg.imgHoverOn, tg.imgHoverOut);
    }
    
    tg.setupGalleryHoverEvent = function(){
        jq(tg.selectors.galleryViewSelector).hover(
            function(){ jq(tg.selectors.mediaGuideSelector).fadeIn('normal'); },
            function(){ jq(tg.selectors.mediaGuideSelector).fadeOut('normal'); }
        );
    };
    
    tg.add = function(image){
        var lastImage = jq(tg.selectors.carouselImgSelector + ":last")[0];
        var index = parseInt(getKssAttr(lastImage, 'index')) + 1;

        var carouselimg = jq('<img class="kssattr-index-' + index + 
                             '" src="' + image.thumb_url + '"  />');

        tg.jcar.add(index+1,  carouselimg);
        tg.addImgEvents(carouselimg);
        
        var description = (image.description == null) ? '' : image.description;
        
        var imagehtml = '<div class="image kssattr-link-' + image.link + ' kssattr-index-' + index + '">' +
			'<img src="' + image.image_url + '" />' +
			'<h2>' + image.title + '</h2>' +
			'<p>' + description + '</p>' +
		'</div>';
		jq(imagehtml).appendTo(jq(tg.selectors.imagesContainerSelector));
    };
    
    tg.addAll = function(images){
        jq(images).each(function(index, image){
            if(jq("div.kssattr-link-" + image.link).size() == 0){//check if image already added first...
                tg.add(image);
            }
        });
        tg.jcar.size(this.jcar.size() + images.length);
        tg.setInfo();
    };
    
    tg.addImages = function(){
        var callback = function(data){

            if(data.doneLoading == "True"){
                //should stop anymore ajax call attempts
                tg.doneLoading = true;
            }
            tg.addAll(data.images);
            jq('div#plone-true-gallery').removeClass('kssattr-imagePage-' + data.page);
            jq('div#plone-true-gallery').addClass('kssattr-imagePage-' + (parseInt(data.page)+1));
            tg.requestInProgress = false;
        };
        
        if(!tg.requestInProgress){
            tg.requestInProgress = true;
            jq.getJSON(
                'loadImagePage', 
                {page: getKssAttr(jq('div#plone-true-gallery'), 'imagePage')}, 
                callback
            );
        }
    };
    
    tg.initialize(element, options);
};