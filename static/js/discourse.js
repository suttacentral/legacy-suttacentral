sc.discourse = {
    forumUrl: 'https://discourse.suttacentral.net',
    shouldNotify: null,
    init: function() {
        var self = sc.discourse,
            conversationCount = $('#discourse-search-results').find('li').length;
        if (conversationCount > 9) {
            conversationCount = '9+';
        }
        self.visible =  $('#discourse-search-results').css('display') != 'none' ;
        $('#discourse-link-button').on('click', function(e) {
            e.preventDefault();
            self.visible = !self.visible;
            if (self.visible) {
                self.show();
            } else {
                self.hide();
            }
            return false
        }).append('<span class="count">{}</span>'.format(conversationCount));
        
        if ("Notification" in window) {
            self.shouldNotify = localStorage.getItem('sc.discourse.shouldNotify') == "true";
            var check = $('<div class="notify-check-wrap"><input type="checkbox"> Notify me of discussions.</div>')
                            .appendTo('#discourse-search-results')
                            .find('input');
            if (self.shouldNotify) {
                check.prop('checked', self.shouldNotify);
            }
            check.on('change', function(e) {
                self.shouldNotify = $(this).prop('checked');
                localStorage.setItem('sc.discourse.shouldNotify', self.shouldNotify);
                if (self.shouldNotify) {
                    self.notifyRequest();
                }
            })
            if (self.shouldNotify) {
                self.notify();
            }
        }
    },
    show: function(){
        $('#discourse-search-results').slideDown();
        $('#discourse-search-results ~ *').slideUp()
    },
    hide: function() {
        $('#discourse-search-results').slideUp()
        $('#discourse-search-results ~ *').slideDown()
    },
    notifyRequest: function() {
        var self = this;
        Notification.requestPermission();
    },
    notify: function() {
        if (!("Notification") in window) {
            return
        }
        
        var count = $('#discourse-search-results').find('li').length,
            n = new Notification("Discourse",
                {
                    body: "There are {} discissions about {}".format(count, sc.exports.uid),
                    icon: "/img/apple-touch-icon-114x114-precomposed.png"
                });
            n.onclick = function() {
                sc.sidebar.show();
                $('#discourse-link-button').click();
            }
            setTimeout(n.close.bind(n), 7000);
            $(window).unload(n.close.bind(n));
        
    }
}


var discourseWrapper = $('#discourse-results-wrapper');
if (discourseWrapper.length) {
    var url = window.location.origin + '/en/' + sc.exports.uid + '/discussion';
    $.ajax(url, {cache: true, dataType: 'html'})
     .then(function(data) {
         discourseWrapper[0].outerHTML = data;
         sc.discourse.init();
     });
}

