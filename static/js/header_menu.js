sc.headerMenu = {
    lastScreenScroll: 0,
    animationDone: true,
    toggle: function(e){
        $(this).toggleClass('active');
        $('header .pitaka_menu').not(this).removeClass('active')
    },
    init: function() {
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
                    $('#menu').removeClass('search-box-popup');
                });
                //  Fire off the transition animation by adding the class (see handler above)
                $('#page-header-search input').addClass('collapse-effect');
            });
        });

        $('#panel-screen-wrap').on('click', function(e) {
            if ($(e.target).is('a'))
                return true;
            if ($("#autocomplete-dropdown").is(":visible")) {
                $('#panel-screen-wrap').removeClass('active');    //  if search drop down is visible, remove shadow box
            } else {
                sc.headerMenu.update($(e.target));
            }
            return false
        }).on('mousewheel', function(e){
            if (e.target == this) {
                // sc.headerMenu.hideAll();
                sc.headerMenu.update($(e.target));
                return false;
            }
            return true
        })

        $('[name=header-pinned]').on('click', sc.headerMenu.togglePinHeader);
        if (localStorage.getItem('sc.headerMenu.pinned')){
            $('main').addClass('header-pinned');
        };
            
        $(window).on('ready resize', sc.headerMenu.adjustColumns);
        $(window).scroll(sc.headerMenu.scrollShowHide);
        $('#panel').scrollLock();

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
            $('#panel-screen-wrap, #panel').addClass('active');
            target.addClass('active');
            element.addClass('active');
            setTimeout(self.adjustColumns, 50);
        }
    },

    togglePinHeader: function(e) {
        var isPinnedH = ($('[name=header-pinned]').prop('checked') == true);
        console.log('Pinned Header = ' + isPinnedH);
        
        if (isPinnedH) {
            localStorage.setItem('sc.headerMenu.pinned', true);
            $('main').addClass('header-pinned');
        } else {
            localStorage.removeItem('sc.headerMenu.pinned');
            $('main').removeClass('header-pinned');
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
    scrollShowHide: function(e){
        var self = sc.headerMenu,
            scrollTop = $("body").scrollTop() || $("html").scrollTop(),
            scrollAmount = scrollTop - self.lastScreenScroll,
            header = $('header');
            
        self.lastScreenScroll = scrollTop;
        if (scrollTop <= 10) {
            header.removeClass('retracted');
            return
        }

        if (scrollAmount > 0) {
            var isHPinned = localStorage.getItem('sc.headerMenu.pinned');
            if (!isHPinned && !header.hasClass('retracted')) {
                header.addClass('retracted');
                self.hideAll();
            }
            return
        }
        
        var now = e.timeStamp;
        if (scrollAmount < 0) {
             header.removeClass('retracted');
             return
        }
    }
}


$(document).ready(function(){
    function proceed(panelData) {
        if ($('#panel-placeholder').length) {
            $('#panel-placeholder')[0].outerHTML = panelData;
        }
        sc.headerMenu.init();
    }
    var panelData = localStorage.getItem('sc.panel-data'),
        panelTime = localStorage.getItem('sc.panel-time'),
        nowTime = new Date().getTime();
    console.log('Panel Data : ' + (panelData ? panelData.length : undefined));
    if (!panelData || nowTime - panelTime > (86400 * 7)) {
        $.ajax('/panel', {
            cache: true,
            dataType: 'html'
        }).then(function(panelData) {
            localStorage.setItem('sc.panel-data', panelData);
            localStorage.setItem('sc.panel-time', nowTime);
            proceed(panelData);
        }, function(){
            // Useful for offling browsing
            if (panelData) {
                proceed(panelData);
            }
        });
    } else {
        proceed(panelData);        
    }
    
        
})
    
