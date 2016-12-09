import json
import thread

from TweetListener import *
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, send, emit
from TweetHandler import TwitterHandler
import requests



# function that pulls tweets from twitter
def startTwitterRequests():
    startStream()

def persistTweet(tweet):
    tweeter = TwitterHandler()
    print('*****************************************************************')
    # print(type(tweet))
    print('*****************************************************************')
    json_msg = json.loads(tweet['Message'])
    #json_msg = json.dumps(msg)
    tid = json_msg['id']
    location_data = json_msg['location']
    message = json_msg['message']
    author = json_msg['author']
    timestamp = json_msg['timestamp']
    sentiment = json_msg['alchemy_response']['type']
    # print (type(sentiment))    

    # print(tid)
    # print(location_data)
    # print (message)
    # print(author)
    # print (timestamp)
    # print (sentiment)
    # print('*****************************************************************')
   # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

    response = tweeter.insertTweet(tid, location_data, message, author, timestamp, sentiment)
     
    # print tweet['Message']
    # print (type(tweet['Message']))
    print json_msg
    # print (type(json_msg))
    # print msg['author']
    #print json_msg
    #print (type(json_msg))
    print('*****************************************************************')

    return response
    
# EB looks for an 'application' callable by default.
application = Flask(__name__)
socketio = SocketIO(application)

@application.route('/')
def api_root():
    return render_template('index.html')
    # return 'Welcome'

@application.route('/search/sns', methods = ['GET', 'POST', 'PUT'])
def snsFunction():
    
    try:
        notification = json.loads(request.data)
    except:
        print("Unable to load request")
        pass

    headers = request.headers.get('X-Amz-Sns-Message-Type')
    print(notification)

    if headers == 'SubscriptionConfirmation' and 'SubscribeURL' in notification:
        url = requests.get(notification['SubscribeURL'])
        print(url) 
    elif headers == 'Notification':
        persistTweet(notification)
        socketio.emit('first', {'notification':'New Tweet!'})
    else: 
        print("Headers not specified")

    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    return "OK\n"

@application.route('/search/<keyword>')
def searchKeyword(keyword):
    searchTweets = TwitterHandler()
    result = searchTweets.getTweets(keyword)
    return jsonify(result)

@application.route('/search/<keyword>/<distance>/<latitude>/<longitude>')
def searchKeywordWithDistance(keyword, distance, latitude, longitude):
    searchTweets = TwitterHandler()
    result = searchTweets.getTweetsWithDistance(keyword, distance, latitude, longitude)
    return jsonify(result)


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    thread.start_new_thread(startTwitterRequests, ())
    #application.debug = True
    #application.host = '0.0.0.0'
    #application.port = 5000
    # application.run(host = '0.0.0.0',debug=True, port=5000)
    socketio.run(application, host = '0.0.0.0',debug=True, port=5000)
