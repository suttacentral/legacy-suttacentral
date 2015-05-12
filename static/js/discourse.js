sc.discourse = {
    forumUrl: 'https://discourse.suttacentral.net',
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
        self.fetchCategoryData(self.search);
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
        
        self.jqXHR = $.ajax(self.forumUrl + '/search/query.json', 
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
                catIcon = self.makeCategoryIcon(topic.category_id),
                code = '<li><a href="{}" target="_blank">{}<span class="topic-title">{}</span><span class="post-blurb">{}</span></a></li>'.format(url, catIcon, topic.fancy_title, post.blurb); 
            ul.append(code)            
        })
            
    },
    fetchCategoryData: function(callback) {
        self = sc.discourse;
        var storedData = null,//localStorage.getItem('sc.discourse.categoryData'),
            expires = 7 * 86400 * 1000;
        if (storedData) {
            if (Date.now() - storedData.time > expires) {
                storedData = null;
            }
        }
            
        if (!storedData) {
            $.ajax(self.forumUrl + '/categories.json').success(function(data) {
                console.log(data);
                self.categoryData = self.massageCategoryData(data);
                localStorage.setItem('sc.discourse.categoryData', 
                                        {time: Date.now(),
                                         data: self.categoryData})
                callback();
            })
        } else {
            self.categoryData = storedData.data;
            callback();
        }
    },
    massageCategoryData: function(data) {
        var properties = ['id', 'color', 'text_color', 'description_text', 'name', 'subcategory_ids']
        
        var pickedData = _.map(data.category_list.categories, 
                                function(obj){
                                    return _.pick(obj, properties)
                                }
                            )
        
        var out = {}
        _.each(pickedData, function(obj) {
            out[obj.id] = obj;
            _.each(obj.subcategory_ids, function(id) {
                console.log('Setting {} to {}'.format(id, obj.id))
                out[id] = obj;
            });
        });
        return out
    },
    makeCategoryIcon: function(categoryId) {
        var self = this,
            data = self.categoryData[categoryId];
        //Uncategorized
        
        if (!data) return categoryId;
        
        
        var icon = $('<span/>').text(data.name)
                           .addClass('topic-category-icon')
                           .attr('title', data.description_text);
        $('<span class="topic-category-icon-bar"> </span>')
            .css('background-color', '#' + data.color)
            .prependTo(icon);
        return $('<span/>').append(icon).html();
        
        
        
    }
}

if (document.getElementById('text')) {
    $(document).ready(sc.discourse.init)
}
