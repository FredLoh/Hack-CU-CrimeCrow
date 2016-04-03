/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# RUN THE APP:
  Create a Slack app. Make sure to configure the bot user!
    -> https://api.slack.com/applications/new
    -> Add the Redirect URI: http://localhost:3000/oauth
  Run your bot from the command line:
    clientId=<my client id> clientSecret=<my client secret> port=3000 node slackbutton_bot.js
# USE THE APP
  Add the app to your Slack by visiting the login page:
    -> http://localhost:3000/login
  After you've added the app, try talking to your bot!
# EXTEND THE APP:
  Botkit is has many features for building cool and useful bots!
  Read all about it here:
    -> http://howdy.ai/botkit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

/* Uses the slack button feature to offer a real time bot to multiple teams */
var fs = require("fs")
var Botkit = require('botkit');
var os = require('os');

var config = JSON.parse(fs.readFileSync("config.json"))
firebaseStorage = require('./firebase_storage.js')({firebase_uri: config.firebase_uri})
firebaseReportRef = new Firebase(config.firebase_uri + '/reports')

if (!config.client_id || !config.client_secret || !config.port) {
  console.log('Error: Specify clientId clientSecret and port in environment');
  process.exit(1);
}

var controller = Botkit.slackbot({
  debug: true,
    storage: firebaseStorage,
}).configureSlackApp(
  {
    clientId: config.client_id,
    clientSecret: config.client_secret,
    scopes: ['bot'],
  }
);

controller.setupWebserver(config.port,function(err,webserver) {
  controller.createWebhookEndpoints(controller.webserver);

  controller.createOauthEndpoints(controller.webserver,function(err,req,res) {
    if (err) {
      res.status(500).send('ERROR: ' + err);
    } else {
      res.send('Success!');
    }
  });
});


// just a simple way to make sure we don't
// connect to the RTM twice for the same team
var _bots = {};
function trackBot(bot) {
  _bots[bot.config.token] = bot;
}

controller.on('create_bot',function(bot,config) {

  if (_bots[bot.config.token]) {
    // already online! do nothing.
  } else {
    bot.startRTM(function(err) {

      if (!err) {
        trackBot(bot);
      }

      bot.startPrivateConversation({user: config.createdBy},function(err,convo) {
        if (err) {
          console.log(err);
        } else {
          convo.say('I am a bot that has just joined your team');
          convo.say('You must now /invite me to a channel so that I can be of use!');
        }
      });

    });
  }

});


// Handle events related to the websocket connection to Slack
controller.on('rtm_open',function(bot) {
  console.log('** The RTM api just connected!');
});

controller.on('rtm_close',function(bot) {
  console.log('** The RTM api just closed');
  // you may want to attempt to re-open
});

// controller.hears('hello','direct_message',function(bot,message) {
//   bot.reply(message,'Hello!');
// });

controller.storage.teams.all(function(err,teams) {

  if (err) {
    throw new Error(err);
  }

  // connect all teams with bots up to slack!
  for (var t  in teams) {
    if (teams[t].bot) {
      controller.spawn(teams[t]).startRTM(function(err, bot) {
        if (err) {
          console.log('Error connecting bot to Slack:',err);
        } else {
          trackBot(bot);
        }
      });
    }
  }
});


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
  if(message.event == 'direct_message'){
    subscriber = {
      id: message.user,
      type: 'direct_message',
      message: message
    }
  }
  else{
    subscriber = {
      id: message.channel,
      type: 'mention',
      message: message
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
  return {
    id: id,
    title: extractedTitle,
    body: extractedBody,
    location: {
      name: extractedLocation
    }
  }
}

firebaseReportRef.on('child_added', function(childSnapshot, prevChildKey) {
  data = childSnapshot.val()
  var location
  if(data.location != null){
    location ='Location:' + data.location.name
  }
  else{
    location =  ''
  }
  message = data.title + '\n' + data.body + '\n' + location
  controller.storage.subscribers.all(function(err, subscribers) {
    if (subscribers.message)  
      bot.reply(subscribers[0].message, message)
  });
});







