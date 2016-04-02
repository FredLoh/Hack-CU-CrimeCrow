
if (!process.env.token) {
  console.log('Error: Specify token in environment');
  process.exit(1);
}
var botkit = require('botkit')
var Firebase = require('firebase');
var fs = require('fs')
var os = require('os')
var request = require('request')
var wait = require('wait.for')

var config = JSON.parse(fs.readFileSync('config.json'))
firebaseStorage = require('./firebase_storage.js')({firebase_uri: config.firebase_uri})
firebaseReportRef = new Firebase(config.firebase_uri + '/reports')

var controller = botkit.slackbot({
  debug: true,
  storage: firebaseStorage
});

var bot = controller.spawn({
  token: process.env.token
}).startRTM();


controller.hears(['hello', 'hi'], 'direct_message,direct_mention,mention', function(bot, message) {

  bot.reply(message, 'Hi! your friendly, neighbourhood reporting bot here');
  bot.reply(message, 'Type help if you need assistance!')
});

controller.hears(['help', 'assistance'], 'direct_message,direct_mention,mention', function(bot, message) {

  bot.reply(message, 'Heard you need some help!');
  bot.reply(message, '"report" to report an incident\n"title" for the title of the incident and\n"location" for well it\'s location' )
  bot.reply(message, 'Example report:\nreport: A gun shooting in San Pedro killed 7 individuals title: 7 killed in San Pedro location: Rio Tigris, San Pedro')

});

controller.hears(['report:',], 'direct_message,direct_mention,mention', function(bot, message) {
  var extractedReport = extractReport(message.user + message.ts.replace('.', ''), message.text)
  controller.storage.reports.save(extractedReport, function(err, id) {
    bot.reply(message, 'Incident reported')
  });
});

controller.hears(['unsubscribe'], 'direct_message,direct_mention,mention', function(bot, message) {
  console.log(message)
  var id
  if(message.event = 'direct_message')
    id= message.user
  else
    id= message.channel
  controller.storage.subscribers.remove(id, function(err, id) {
  });
  bot.reply(message, 'You have been unsubscribed if you were already subscribed\nto subscribe to updates type "subscribe"')

})


controller.hears(['subscribe'], 'direct_message,direct_mention,mention', function(bot, message) {
  console.log(message)
  var subscriber
  if(message.event = 'direct_message'){
    subscriber = {
      id: message.user,
      type: 'direct_message'
    }
  }
  else{
    subscriber = {
      id: message.channel,
      type: 'mention'
    }
  }
  controller.storage.subscribers.save(subscriber, function(err, subscriber) {
    bot.reply(message, 'You have been subscribed to updates\nto unsubscribe type "unsubscribe"')
  });

})

function extractReport(id, text){
  var splitText = text.split('title: ')[0]
  var extractedBody = text.split('title: ')[0].replace('report:', '').trim()
  var extractedTitle = text.split('title: ')[1].split('location: ')[0].trim()
  var extractedLocation = text.split('location: ')[1].trim()
  setTimeout(function() {
  getLocation(id, extractedLocation)
}, 3000);
  return {
    id: id,
    title: extractedTitle,
    body: extractedBody,
    location: {
      name: extractedLocation
    }
  }
}


function getLocation(key, location){
  controller.storage.reports.get(key, function(err, report) {
    query = config.google_maps_geocoding_uri + 'address=' + location.replace(/ /g, '+') + '&key=' + config.google_maps_api_key
    console.log(query)
    request(query , function (error, response, body) {
      if (!error && response.statusCode == 200) {
        response = JSON.parse(body)
        console.log(response)
        latlng = response.results[0].geometry.location
        report.location.lat = latlng.lat
        report.location.lng = latlng.lng
        controller.storage.reports.save(report, function(err, id) {
        });
      }
    })
  })
}

firebaseReportRef.on("value", function(snapshot) {
  data = snapshot.val()
  message = data.title + '\n' + data.body + '\n' + 'Location:' + data.location
  controller.storage.subscribers.all(function(subscribers){
    for(subscriber in subscribers){
      if(subscriber.channel){
        bot.say(
        {
          text: message,
          channel: channel.id
        }
        )
      };
    }
  })
})




