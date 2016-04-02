var Firebase = require('firebase');

/**
 * The Botkit firebase driver
 *
 * @param {Object} config This must contain a `firebase_uri` property
 * @returns {{teams: {get, save, all}, channels: {get, save, all}, users: {get, save, all}}}
 */
 module.exports = function(config) {

    if (!config || !config.firebase_uri) {
        throw new Error('firebase_uri is required.');
    }

    var rootRef = new Firebase(config.firebase_uri)
    teamsRef = rootRef.child('slack/teams')
    usersRef = rootRef.child('slack/users')
    channelsRef = rootRef.child('slack/channels')
    reportsRef = rootRef.child('reports')
    subscribersRef = rootRef.child('slack/subscribers')

    return {
        teams: {
            get: get(teamsRef),
            save: save(teamsRef),
            all: all(teamsRef),
            remove: remove(teamsRef)
        },
        channels: {
            get: get(channelsRef),
            save: save(channelsRef),
            all: all(channelsRef),
            remove: remove(channelsRef)
        },
        users: {
            get: get(usersRef),
            save: save(usersRef),
            all: all(usersRef),
            remove: remove(usersRef)
        },
        reports:{
            get: get(reportsRef),
            save: save(reportsRef),
            all: all(reportsRef),
            remove: remove(reportsRef)
        },
        subscribers:{
            get: get(subscribersRef),
            save: save(subscribersRef),
            all: all(subscribersRef),
            remove: remove(subscribersRef)
        }
    };
};

/**
 * Given a firebase ref, will return a function that will get a single value by ID
 *
 * @param {Object} firebaseRef A reference to the firebase Object
 * @returns {Function} The get function
 */
 function get(firebaseRef) {
    return function(id, cb) {
        firebaseRef.child(id).once('value', success, cb);

        function success(records) {
            if(records.val() == null){
                cb(Error("Object not found"))
            }
            else{
                cb(null, records.val());
            }
        }
    };
}

/**
 * Given a firebase ref, will return a function that will save an object. The object must have an id property
 *
 * @param {Object} firebaseRef A reference to the firebase Object
 * @returns {Function} The save function
 */
 function save(firebaseRef) {
    return function(data, cb) {
        var firebase_update = {};
        firebase_update[data.id] = data;
        firebaseRef.update(firebase_update, cb);
    };
}

/**
 * Given a firebase ref, will return a function that will return all objects stored.
 *
 * @param {Object} firebaseRef A reference to the firebase Object
 * @returns {Function} The all function
 */
 function all(firebaseRef) {
    return function(cb) {
        firebaseRef.once('value', success, cb);

        function success(records) {
            var results = records.val();

            if (!results) {
                return cb(null, []);
            }

            var list = Object.keys(results).map(function(key) {
                return results[key];
            });

            cb(null, list);
        }
    };
}

/**
 * Given a firebase ref, will return a function that will remove a single value by ID
 *
 * @param {Object} firebaseRef A reference to the firebase Object
 * @returns {Function} The remove function
 */
 function remove(firebaseRef) {
    return function(id, cb) {
        firebaseRef.child(id).remove();

        function success(records) {
            cb(null, records.val());
        }
    };
}