var worker = new Worker('/js/palilookup/worker.js');







var msgcounter = 0,
    messageIdRegistry = {};

function postLookupMessage(query) {
    query.id = msgcounter;
    msgcounter += 1;
    var deferred = $.Deferred();
    messageIdRegistry[query.id] = deferred;
    console.log('Sending message: ' + JSON.stringify(query));
    worker.postMessage(query);
    return deferred.promise();
}
    
worker.addEventListener('message', function(event) {
    var result = event.data,
        id = result.id;
    
    var deferred = messageIdRegistry[id];
    if (!deferred) {
        console.log('Message not found: ' + id, event.data);
    } else {
        deferred.resolve(result);
    }
    console.log('Worker said: ', event.data);
}, false);


worker.postMessage('Hello');

//var worker = new SharedWorker('/js/palilookup/worker.js');
//worker.port.start();

//worker.port.onmessage = function(event) {
    //console.log('Worker responded with ', event.data);
//}

//worker.onerror = function(a,b) {
    //console.log('Worker Error: ');
    //console.log(a,b);
//}
