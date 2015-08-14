/* This code is based on code from the following blog post
 * http://sravi-kiran.blogspot.com/2014/01/CreatingATodoListUsingIndexDbAndPromise.html
 */

function IDBCache(name, version){
    this.name = name;
    this.version = version;
    this.available = false;
    this.open();
}

IDBCache.prototype = {
    open: function() {
        var self = this,
            version = this.version,
            name = this.name;
            
        var promise = new Promise(function(resolve, reject){
            //Opening the DB
            var request = indexedDB.open(name + "Data", version);      
     
            //Handling onupgradeneeded
            //Will be called if the database is new or the version is modified
            request.onupgradeneeded = function(e) {
                var db = e.target.result;
                e.target.transaction.onerror = indexedDB.onerror;
     
                //Deleting DB if already exists
                if(db.objectStoreNames.contains(name)) {
                    db.deleteObjectStore(name);
                }
                //Creating a new DB store with a paecified key property
                var store = db.createObjectStore(name,
                    {keyPath: "id"});
            };
     
            //If opening DB succeeds
            request.onsuccess = function(e) {
                self.db = e.target.result;
                self.available = true;
                resolve();
            };
     
            //If DB couldn't be opened for some reason
            request.onerror = function(e){
                reject("Couldn't open DB");
            };
        });
        return promise;
    },
    add: function(key, value) {
        //Creating a transaction object to perform read-write operations
        var store = this.db.transaction([this.name], "readwrite").objectStore(this.name);
        
        //Wrapping logic inside a promise
        var promise = new Promise(function(resolve, reject){
            //Sending a request to add an item
            var request = store.put({
                "id": key,
                "data": value
            });
                 
            //success callback
            request.onsuccess = function(e) {
                resolve();
            };
                 
            //error callback
            request.onerror = function(e) {
                console.log(e.value);
                reject("Couldn't add the passed item");
            };
        });
        return promise;
    },
    get: function(key, value) {
        //Creating a transaction object to perform read-write operations
        var store = this.db.transaction([this.name], "readonly").objectStore(this.name);
             
        //Wrapping logic inside a promise
        var promise = new Promise(function(resolve, reject){
            //Sending a request to add an item
            var request = store.get(key);
                 
            //success callback
            request.onsuccess = function(e) {
                if (request.result === undefined) {
                    reject("Not found")
                } else {
                    resolve(request.result);
                }
            };
                 
            //error callback
            request.onerror = function(e) {
                console.log(e.value);
                reject("Couldn't add the passed item");
            };
        });
        return promise;
    }
}
