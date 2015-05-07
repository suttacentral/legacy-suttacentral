sc.discourse = {
    resultsDiv: $('#discourse-search-results'),
    button: $('#discourse-link-button'),
    init: function() {
        var self = sc.discourse;
        self.visible = self.resultsDiv.css('display') != 'none' ;
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
        self.search()
    },
    show: function(){
        self.resultsDiv.slideDown();
        $('#discourse-search-results ~ *').slideUp()
    },
    hide: function() {
        self.resultsDiv.slideUp()
        $('#discourse-search-results ~ *').slideDown()
    },
    search: function() {
        self = sc.discourse;
        if (self.jqXHR) return
        
        self.jqXHR = $.ajax('http://discourse.suttacentral.net/search/query.json', 
                            {
                                data: {
                                    term: '"{}"|{}'.format(sc.text.acro, sc.text.uid),
                                    include_blurbs: true
                                }
                            }).success(self.updateResults)
                              .error(function(){self.button.off('click')});
        
    },
    updateResults: function(data) {
        
        var self = sc.discourse,
            ul = $('<ul class="results"/>');
        
        $('#discourse-search-loading').remove();
        self.resultsDiv.append(ul);
        
        
        self.data = data;
        
        _.zip(data.topics, data.posts).forEach(function(pair){
            var topic = pair[0],
                post = pair[1],
                url = 'http://discourse.suttacentral.net/t/{}/{}/{}'.format(topic.slug, topic.id, post.post_number),
                code = '<li><a href="{}"><span class="topic-title">{}</span><span class="post-blurb">{}</span></a></li>'.format(url, topic.fancy_title, post.blurb); 
            ul.append(code)            
        })
            
    }
}

if (document.getElementById('text')) {
    $(document).ready(sc.discourse.init)
}
