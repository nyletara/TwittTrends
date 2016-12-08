import json
import thread

from TweetListener import *
from flask import Flask, render_template, jsonify, request
import requests
from TweetHandler import TwitterHandler


# function that pulls tweets from twitter
def startTwitterRequests():
    startStream()

def persistTweet(tweet):
    tweeter = TwitterHandler()
    
    tid = tweet['id']
    location_data = tweet['location_data']
    message = tweet['message']
    author = tweet['author']
    timestamp = tweet['timestamp']

    response = tweeter.insertTweet(tid, location_data, message, author, timestamp)
    return response
    
# EB looks for an 'application' callable by default.
application = Flask(__name__)

@application.route('/')
def api_root():
    return render_template('index.html')
    # return 'Welcome'

@application.route('/search/sns')
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
    else: 
        print("Headers not specified")

    return "SNS Notification Recieved\n"

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
    application.run(host='0.0.0.0', port=5000)
