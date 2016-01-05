/* This code is based on code from the following blog post
 * http://sravi-kiran.blogspot.com/2014/01/CreatingATodoListUsingIndexDbAndPromise.html
 */

function IDBCache(name, version){
    this.name = name;
    this.dbname = '_idb_cache_' + name;
    this.version = version;
    this.available = false;
    this.open();
}

IDBCache.prototype = {
    open: function() {
        var self = this,
            version = this.version;
            
        var promise = new Promise(function(resolve, reject){
            //Opening the DB
            var request = indexedDB.open(self.dbname, version);      
            console.log('Opening Database named ' + self.dbname);
     
            //Handling onupgradeneeded
            //Will be called if the database is new or the version is modified
            request.onupgradeneeded = function(e) {
                console.log('Update Needed')
                var db = e.target.result;
                e.target.transaction.onerror = indexedDB.onerror;
     
                //Deleting DB if already exists
                if(db.objectStoreNames.contains(self.name)) {
                    db.deleteObjectStore(self.name);
                }
                //Creating a new DB store with a paecified key property
                var store = db.createObjectStore(self.name,
                    {keyPath: "id"});
            };
     
            //If opening DB succeeds
            request.onsuccess = function(e) {
                console.log('Success opening Database')
                self.db = e.target.result;
                self.available = true;
                resolve();
            };
     
            //If DB couldn't be opened for some reason
            request.onerror = function(e){
                console.log('Error opening Database')
                reject("Couldn't open DB");
            };
        });
        return promise;
    },
    destroy: function() {
        var promise = new Promise(function(resolve, reject) {
            var req = indexedDB.deleteDatabase(this.dbname);
            req.onsuccess = resolve
            req.onerror = reject
            req.onblocked = function() {
                console.log("Delete Operation Blocked");
                reject();
            }
        })
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
