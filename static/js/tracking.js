/* Event Tracking
 *
 * Track events so we know what features are being used, and can
 * identify where effort should be put into development, either
 * through identifying problems or by focusing on the most
 * used features.
 *
 * Note no user-identifiable data is sent to Google.
 * 
 * */

sc.trackEvent = function(params) {
    if (typeof(params) == 'string') {
        params = {
            category: 'button',
            action: 'click',
            label: params
        }
    }
    if ('ga' in window) {
        ga('send', {
            hitType: 'event',
            eventCategory: params.category,
            eventAction: params.action,
            eventLabel: params.label,
            eventValue: params.value
        })
    } else {
        console.log('Event: Category="{}", Action="{}", Label="{}", Value="{}"'.format(params.category, params.action, params.label, params.value || 0));
    }
}

/* Event Tracking */

/* Track Downloads */
$('main').on('click contextmenu', '.file', function(){
    sc.trackEvent({category: 'download',
                    action: 'click',
                    label: $(this).attr('href')});
})


// Track usage of sidebar controls
$('#controls-tab').on('click', '.button', function(e){
    var value = $(e.target).attr('id') || $(e.target).text();
    if ($(this).is('select')) {
        value += '-' + this.value;
    }
    sc.trackEvent(value)
});
