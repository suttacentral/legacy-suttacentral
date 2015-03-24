sc.text_image = {
    isInit: false,
    init: function(){
        if (this.isInit) return
        this.isInit = true;
        if ($('#text').length == 0) {
            return
        }
        var volpage_links = $(sc.classes.marginSelector);
        
        var uid = $('section.sutta').attr('id'),
            ids = volpage_links.map(function(){return $(this).attr('id')}).toArray().join(',');
        
        $.ajax('/data?' + $.param({text_images: 1, 
                                   uid: uid,
                                   volpage_ids: ids})
            ).success(sc.text_image.processData);
        
    },
    processData: function(data, status, jqXHR) {
        console.log(data);
        _.each(data.text_images, function(url, id, _data) {
            console.log(id, url);
            // getElementById doesn't require escaping. unlike $('#...')
            var e = $(document.getElementById(id)),
                link = $('<span/>'),
                offset = e.offset();
            e.after(link);
            link.attr({'data-src': url,
                       'class': 'text-image-button',
                       'title': 'View Page Image'})
                .on('click', sc.text_image.showImage)
            offset.left += e.outerWidth();
            link.offset(offset);
            link.css({'margin-top': '-0.5em',
                      'margin-left': '0.5em'});
        });
    },
    showImage: function(e) {
        var $target = $(e.currentTarget),
            src = $target.attr('data-src'),
            overlay,
            fadeTime = 200;
        e.preventDefault(true);
            
        overlay = $('<div id="text-image-overlay"/>')
            .append($('<div id="text-image"/>')
                .append($('<img/>').attr('src', src)));
        $('main').append(overlay);
        overlay.hide().fadeIn(fadeTime);
        
        var originalWindowScroll = $(window).scrollTop();
        function removeOverlay() {
            overlay.fadeOut(fadeTime, function() {
                overlay.remove();
            });
        }
        overlay.on('click', function(e){
            if (e.target == overlay[0]) {
                removeOverlay();
            }
        });
        
        $(window).on('scroll.sc-text-image', function(e){
            if ((Math.abs($(window).scrollTop() - originalWindowScroll)) > 150 ) {
                removeOverlay()
                $(window).off('scroll.sc-text-image');
            }
        });

        return true;
    }
}

if (sc.userPrefs.getPref("textInfo") === true) {
    sc.text_image.init();
}
