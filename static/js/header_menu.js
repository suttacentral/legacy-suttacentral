sc.headerMenu = {
    node: $('#panel-screen-wrap, #panel'),
    lastScreenScroll: 0,
    animationDone: true,
    toggle: function(e){
        $(this).toggleClass('active');
        $('header .pitaka_menu').not(this).removeClass('active')
    },
    update: function(element, mode) {
        var self = sc.headerMenu,
            target = $(element.find('[href]').attr('href'));

        if (target.length < 1) {
            target = element;
        }

        if (mode === undefined && target.hasClass('active')) {
            mode = "hide";
        } else {
            mode = "show";
        }

        if (mode == "hide") {
            $('#panel').one("transitionend webkitTransitionEnd oTransitionEnd MSTransitionEnd", function(e){
                if (!animationDone && $(e.currentTarget).hasClass('active')) {
                    self.hideAll();
                    animationDone = true;
                }
            });
            if (animationDone) {
                animationDone = false;
                $('#panel-screen-wrap').removeClass('active');
                $('#panel').css({'height': 0});
            }
        }
        else {
            animationDone = true;
            self.hideAll();
            self.node.addClass('active');
            target.addClass('active');
            element.addClass('active');
            setTimeout(self.adjustColumns, 50);
        }
    },
    hideAll: function(e){
        $('#panel  .active, header  .active').removeClass('active');
        $('#panel-screen-wrap, #panel').removeClass('active');
    },
    adjustColumns: function(){
        /* This function is responsible for tweaking the column widths and alignment on the
         * home page creating a very fluid experience
         */
        

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
    scrollEvents: [],
    scrollShowHide: function(e){
        var self = sc.headerMenu,
            scrollTop = $(document.body).scrollTop(),
            scrollAmount = scrollTop - self.lastScreenScroll;
        
        self.lastScreenScroll = scrollTop;
        if (scrollAmount > 0) {
            $('header').addClass('retracted');
            self.hideAll();
            return
        }
        
        if (scrollTop == 0) {
            $('header').removeClass('retracted');
            return
        }
        
        var now = e.timeStamp;
        if (scrollAmount < -3) {
             $('header').removeClass('retracted');
             return
        }
        // if (scrollAmount < 0) {
        //     for (i = self.scrollEvents.length - 1; i >= 0 ; i--) {
        //         oldE = self.scrollEvents[i];
                
        //         var diff = now - oldE[1];
        //         if (diff > 500) {
        //             self.scrollEvents.pop()
        //         } else if (diff > 100 && oldE[0] < 0) {
        //              $('header').removeClass('retracted');
        //              return
        //          }
        //     }
        // }
        

        self.scrollEvents.push([scrollAmount, e.timeStamp]);

    }
}


setTimeout(function(){
    $('header .pitaka_menu a').each(function(){
        $(this).attr('href', '#' + $(this).attr('href').replace(/^\.*\//, '').replace('.html', ''));
    });
    $('header .pitaka_menu').on('click', function(){sc.headerMenu.update($(this)); return false});

    //  If click on the search-popup-btn, then add classes to configure the layout properly
    $('.search-popup-btn').on('click', function() {
        $('#menu').addClass('search-box-popup');
        $('#page-header-search input').focus();
        $('#page-header-search input').one('focusout', function(event) {
            // on focusout, setup a handler to be called on the input box *after* the transition animations complete
            $('#page-header-search input').one("transitionend webkitTransitionEnd oTransitionEnd MSTransitionEnd", function(e){
                $('#page-header-search input').removeClass('collapse-effect');
                // Lets now remove the 'searc' class (after .25 seconds to make sure search is triggered properly)
                // setTimeout(function() {
                    $('#menu').removeClass('search-box-popup');
                // }, 250);
            });
            //  Fire off the transition animation by adding the class (see handler above)
            $('#page-header-search input').addClass('collapse-effect');
        });
    });

    $('#panel-screen-wrap').on('click', function(e) {
        if ($(e.target).is('a'))
            return true;
        // sc.headerMenu.hideAll();
        sc.headerMenu.update($(e.target));
        return false
    }).on('mousewheel', function(e){
        if (e.target == this) {
            // sc.headerMenu.hideAll();
            sc.headerMenu.update($(e.target));
            return false;
        }
        return true
    })
        
    $(window).on('ready resize', sc.headerMenu.adjustColumns);
    $(window).scroll(sc.headerMenu.scrollShowHide);
    $('#panel').scrollLock();
});
    
