sc.headerMenu = {
    activate: function(e){
        $(this).addClass('active');
    },
    deactivate: function(e) {
        $(this).removeClass('active');
    }
    ,
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
            $('#panel-screen-wrap').show()
            target.addClass('active');
            element.addClass('active');
        }
    },
    hideAll: function(e){
        $('#panel  .active, header  .active').removeClass('active');
        $('#panel-screen-wrap').hide();
    }
        
}


setTimeout(function(){
    $('header nav').on('click', function(){sc.headerMenu.update($(this));});
    $('#panel-screen-wrap').on('click', sc.headerMenu.hideAll);
    //$('#panel').on('click', function(e){e.stopPropagation()});
    console.log('Okay');
}, 10);
