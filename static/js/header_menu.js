sc.headerMenu = {
    lastScreenScroll: 0,
    activate: function(e){
        $(this).addClass('active');
    },
    deactivate: function(e) {
        $(this).removeClass('active');
    },
    toggle: function(e){
        $(this).toggleClass('active');
        $('header nav').not(this).removeClass('active')
    },
    update: function(element, mode) {
        console.log('Hi There!');
        var self = sc.headerMenu,
            target = $(element.find('[href]').attr('href'));
        
        
        if (mode === undefined && target.hasClass('active')) {
            mode = "hide";
        } else {
            mode = "show";
        }

        console.log(mode);
        console.log(target);

        if (mode == "hide") {
            self.hideAll();
        }
        else {
            self.hideAll();
            $('#panel-screen-wrap, #panel').addClass('active')
            target.addClass('active');
            element.addClass('active');
            //$(document.body).addClass('overflow-hidden');
            setTimeout(self.adjustColumns, 50);
        }
    },
    hideAll: function(e){
        $('#panel  .active, header  .active').removeClass('active');
        $('#panel-screen-wrap, #panel').removeClass('active');
        //$(document.body).removeClass('overflow-hidden');
    },
    adjustColumns: function(){
        /* This function is responsible for tweaking the column widths and alignment on the
         * home page creating a very fluid experience
         */
        
        console.log('Adjusting column widths');

        var contents = $('.contents.active'),
            contentsWidth = contents.width(),
            ruler = $('<span>m</span>').appendTo(contents.find('.column li:last')),
            t = contents.find('.column:first'),
            extraWidth = t.outerWidth(true) - t.width(),
            minWidth = ruler.innerWidth() * 12.5 + extraWidth,
            columnWidth = Math.max(minWidth, contentsWidth / 5.25) + extraWidth,
            actualColumnCount = contents.find('.column').length;
        ruler.remove();
        fitColumnCount = Math.floor(contentsWidth / columnWidth);
        columnWidth = contentsWidth / fitColumnCount - 10;
        
        $('#panel').find('.column').css({'width': columnWidth, 'min-width': minWidth});

        var maxHeight = $(window).height() * 0.9 - $('header').height(),
            maxColumnHeight = Math.max.apply(null,
                contents.find('.column')
                        .map(function(){return $(this).offset().top + $(this).outerHeight(true)}))
        panelHeight = Math.min(maxColumnHeight + 5, maxHeight)
        
        $('#panel').css({'height': panelHeight})
    },
    scrollShowHide: function(e){
        var self = sc.headerMenu,
            scrollTop = $(document.body).scrollTop(),
            scrollAmount = scrollTop - self.lastScreenScroll;
        self.lastScreenScroll = scrollTop;
        
        if (scrollTop == 0) {
            $('header').removeClass('retracted');
        }
        else {
            $('header').addClass('retracted');
            self.hideAll();
        }


    }
}


setTimeout(function(){
    $('header nav a').each(function(){
        $(this).attr('href', $(this).attr('href').replace('/', '#'));
    });
    $('header nav').on('click', function(){sc.headerMenu.update($(this)); return false});
    $('#panel-screen-wrap').on('click', function(e) {
        console.log(e.target);
        if ($(e.target).is('a'))
            return true;
        sc.headerMenu.hideAll();
        return false
    }).on('mousewheel', function(e){
        if (e.target == this) {
            sc.headerMenu.hideAll();
            return false;
        }
        return true
    })
        
    $(window).on('ready resize', sc.headerMenu.adjustColumns);
    $(window).scroll(sc.headerMenu.scrollShowHide);
    $('#panel').scrollLock();
});
    
