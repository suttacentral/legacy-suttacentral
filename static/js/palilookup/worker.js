/* SharedWorker for handling Pali Lookup backend stuff */

var start = Date.now();

var window = self;

importScripts('/js/lib/qwest.min.js', '/js/vendor/dexie.min.js', '/js/vendor/underscore-1.8.3.js');


/* Libraries */

function levenshteinDistance(a, b) {
    if(a.length == 0) return b.length; 
    if(b.length == 0) return a.length; 

    var matrix = [];

    // increment along the first column of each row
    var i;
    for(i = 0; i <= b.length; i++){
        matrix[i] = [i];
    }

    // increment each column in the first row
    var j;
    for(j = 0; j <= a.length; j++){
        matrix[0][j] = j;
    }

    // Fill in the rest of the matrix
    for(i = 1; i <= b.length; i++){
        for(j = 1; j <= a.length; j++){
            if(b.charAt(i-1) == a.charAt(j-1)){
                matrix[i][j] = matrix[i-1][j-1];
            } else {
                matrix[i][j] = Math.min(matrix[i-1][j-1] + 1, // substitution
                                    Math.min(matrix[i][j-1] + 1, // insertion
                                        matrix[i-1][j] + 1)); // deletion
            }
        }
    }

    return matrix[b.length][a.length];
}


function postProgress(type, progress) {
    console.log(type, progress);
    self.postMessage({type: type, progress: progress});
}

Dexie.Promise.on('error', function(error) {
    console.error('Uncaught error: ' + error);
    throw error;
});

var db = new Dexie('palilookup2');

db.version(1).stores({
    'entries': 'term',
    'meta': 'key'
});

db.on('ready', function() {
    return db.meta.count(function(count) {
        if (count > 0) {
            console.log('already populated');
        } else {
            console.log('Populating database');
            
            var promise = new Dexie.Promise(function(resolve, reject) {
                qwest.get('/js/data/all_dict.json',
                      null,
                      {
                          cache: true,
                          responseType: 'json'
                      }
                ).then(function(xhr, response) {
                    resolve(response);
                }).catch(function(xhr, response, err) {
                    console.error('Failed to retrieve data : ' + err);
                    throw error
                })
            })
            promise.then(function(data) {
                console.log('Got the data, all ' + data.length + ' entries. Now to add them.');
                return new Dexie.Promise(function(resolve, reject) {
                    var offset = 0,
                        chunkSize = Math.floor(1 + data.length / 100),
                        chunks = [];
                        
                    while (offset < data.length) {
                        chunks.push(data.slice(offset, offset + chunkSize));
                        offset += chunkSize;
                    }
                    loadNextChunk = function() {
                        var chunk = chunks.splice(0, 1)[0];
                        console.log('Adding chunk starting with ' + chunk[0].term);
                        db.transaction('rw', db.entries, function() {
                            chunk.forEach(function(entry) {
                                db.entries.put(entry);
                            })
                        }).then(function(){
                            if (chunks.length > 0 ) {
                                setTimeout(loadNextChunk, 1);
                            } else {
                                db.transaction('rw', db.meta, function(){
                                    db.meta.put({key: 'terms', value: _.pluck(data, 'term')});
                                    db.meta.put({key: 'ready'}).then(resolve);
                                });
                            }
                        }).catch(reject);
                    }

                    console.log('Adding data in ' + chunks.length + ' chunks of ' + chunkSize + ' entries');
                    loadNextChunk();
                });
                    
            }).then(function(){
                console.log('Transaction committed');
            })
        }
    })
})

db.open()
  .catch(function(error) {
      console.error('Error opening IndexedDB database: ' + error);
      throw error
});

var termsPromise = null;


self.addEventListener('message', function(event) {
    console.log('Received Query: ' + JSON.stringify(event.data));
    var query = event.data;
    if (!query) {
        self.postMessage('No query: ' + JSON.stringify(query));
    } else if (query.type == 'terms') {
        getEntriesByTerms(query);
    } else if (query.type == 'fuzzy') {
        getEntriesFuzzy(query);
    } else {
        self.postMessage('Unknown query: ' + JSON.stringify(query));
    }
}, false);

function getEntriesByTerms(query) {
    console.log('New Query: ' + JSON.stringify(query));
    db.entries.where('term').anyOf(query.terms).toArray(function(results){
        self.postMessage({id: query.id, hits: results});        
    })
}

function getEntriesFuzzy(query) {
    if (!termsPromise) {
        termsPromise = db.meta.get('terms');
    }
    termsPromise.then(function(data) {
        var terms = data.value,
            term = query.term,
            rex = null,
            hits = [];
        
        if (query.prefix_length) {
            rex = RegExp('^' + term.slice(0, 2));
        }
        
        var maxEditDistance = Math.floor(term.length / 3);
        
        terms.forEach(function(otherTerm) {
            if (!rex || rex.test(otherTerm)) {
                if (Math.abs(otherTerm.length - term.length) > maxEditDistance) {
                    return
                }
                var editDistance = levenshteinDistance(term, otherTerm);
                if (editDistance <= maxEditDistance) {
                    hits.push({editDistance: editDistance, term: otherTerm});
                }
            }
        })
        
        hits = _.sortBy(hits, 'editDistance');
        hits = _.pluck(hits, 'term');
        
        getEntriesByTerms({id: query.id, terms: hits});
    })
}


/*
function addAllEntriesToDatabase(entries, db) {
    console.log('adding entries to database');
    try {
        var promise = new Promise(function(resolve, reject) {
            function processSlice(offset, sliceSize) {
                chunk = entries.slice(offset, offset + sliceSize);
                addEntriesToDatabase(chunk, db).then(function() {
                    postProgress("loading", offset + '/' + entries.length);
                    if (offset >= entries.length) {
                        resolve();
                    } else {
                        processSlice(offset + sliceSize, sliceSize)
                    }
                })
            }
            
            processSlice(0, 200);
        })
        return promise;
    } catch (e) {
        console.error(e);
        throw error
    }
}

function addEntriesToDatabase(entries, db) {
    console.log('Adding chunk to database');
    return db.transaction("rw", db.entries, function(){
        for (var i = 0; i < data.length; i++) {
            var entry = data[i];
            db.entries.put(entry);
        }
    }).catch(function(error) {
        console.error(error);
        throw error
    });
}

var data = null;




//var port;

//console.log('Loading Worker');
//self.addEventListener('connect', function(event) {
    //console.log('Worker Started');
    //port = e.ports[0];
    //port.onmessage = handleMessage;
    //port.start();
//});

//function handleMessage(event) {
    //console.log('Message Received from main script');
    //console.log(event.data);
    
    //port.postMessage("You sent me data of length " + event.data.length);
//}
*/
