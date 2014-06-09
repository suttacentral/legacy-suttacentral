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
    }
}


$(document).ready(function(){
    $('header nav').on('hover', sc.headerMenu.activate, sc.headerMenu.deactivate)
                    .on('click', sc.headerMenu.toggle);

});
