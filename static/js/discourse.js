sc.discourse = (function(){
    if ($('#text').length == 0) return
    var baseHref = 'http://discourse.suttacentral.net'
    var uid = location.href.match(/\w*$/)[0];
    function init() {
        if ($('#text').length == 0) return
        
        var uid = location.href.match(/\w+$/)[0]
        $.ajax('http://discourse.suttacentral.net/tagger/tag/{}.json'.format(uid)).done(showResults);
        console.log('getting');
    }

    function showResults(data) {
        console.log(data);
        var results = $('#discourse'),
            topics = data.topic_list.topics;

            topics = _.sortBy(topics, 'last_posted_at');
            _.each(topics, function(e){
                results.append($('<p><a href="{}/t/{}">{} ({})</a></p>'.format(
                    baseHref,
                    e.id,
                    e.fancy_title,
                    e.posts_count)));
            })
    }

    init();
    console.log('hi');
})();
