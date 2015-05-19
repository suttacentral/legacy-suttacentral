sc.discourse = {
    forumUrl: 'https://discourse.suttacentral.net',
    button: $('#discourse-link-button'),
    init: function() {
        var self = sc.discourse;
        self.visible =  $('#discourse-search-results').css('display') != 'none' ;
        self.button.on('click', function(e) {
            e.preventDefault();
            self.visible = !self.visible;
            if (self.visible) {
                self.show();
            } else {
                self.hide();
            }
            return false
        })
    },
    show: function(){
        $('#discourse-search-results').slideDown();
        $('#discourse-search-results ~ *').slideUp()
    },
    hide: function() {
        $('#discourse-search-results').slideUp()
        $('#discourse-search-results ~ *').slideDown()
    }
}

if (document.getElementById('text')) {
    $(document).ready(sc.discourse.init)
}
