/* Stores state information
 * This is guaranteed to be available during initialization code
 * and for inline scripts in the HTML.
 * (i.e. it is one of the first loaded scripts)
 *
 * State is stored in memory and comitted to session storage
 * when browsing away from the page.
 */

sc = {
    sessionState: {
        d: {},
        setItem: function(k, v) {
            this.d[k] = v
        },
        getItem: function(k) {
            return this.d[k]
        },
        save: function() {
            window.sessionStorage.setItem('__sc_state', JSON.stringify(sc.sessionState.d))
        },
        load: function() {
            this.d = JSON.parse(window.sessionStorage.getItem('__sc_state') || '{}')
        }
    }
}
window.onunload = sc.sessionState.save;
sc.sessionState.load();
