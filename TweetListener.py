# -*- coding: utf-8 -*-
import traceback
import tweepy
import json
import boto3
import time
import ConfigParser
from tweepy import Stream
from tweepy.streaming import StreamListener
from TweetHandler import TwitterHandler
from AmazonSQSServices import SQSServices
from AmazonSNSServices import SNSServices
from ElasticSearchServices import ElasticSearchServices
from watson_developer_cloud import AlchemyLanguageV1

config = ConfigParser.ConfigParser()
config.readfp(open(r'./configurations.txt'))

consumerKey=config.get('API Keys', 'consumerKey')
consumerSecret=config.get('API Keys', 'consumerSecret')
accessToken=config.get('API Keys', 'accessToken')
accessSecret=config.get('API Keys', 'accessSecret')
alchemyAPIKey=config.get('API Keys', 'accessAlchemy')

KEYWORDS = ['chelsea', 'premier', 'pokemon', 'fruit', 'food', 'coffee', 'pizza', 'california']
REQUEST_LIMIT = 420

try:
    sqs_queue = SQSServices()
    sqs = boto3.resource('sqs')
    # print(sqs_queue.createQueue('twitterTrends'))
except Exception as e:
    print("Queue twitterTrends already exists")
    # print(sqs_queue.getQueueName('twitterTrends'))

try:
    sns = boto3.client('sns')
    # sns_service = SNSServices()
except Exception as e:
    print("SNS service already established")

print(alchemyAPIKey)
alchemy = AlchemyLanguageV1(api_key=alchemyAPIKey)

collection = {
	"mappings": {
		"finaltweets2": {
			"properties": {
				"id": {
					"type": "string"
				},
				"message": {
					"type": "string"
				},
				"author": {
					"type": "string"
				},
				"timestamp": {
					"type": "string"
				},
				"location": {
					"type": "geo_point"
				}, 
                                "sentiment": {
                                        "type": "string"
                                }
			}
		}
	}
}

index = "finaltwittermapindex5"
try:
    collection_service = ElasticSearchServices()
    collection_service.create_collection(index, collection)
except:
    print "Index already created"

class TweetListener(StreamListener):

    def on_data(self, data):
        try:
            parse_data(data)
            processData()
        except:
            pass
            # print("")
            # print("No location data found")
        return(True)

    def on_error(self, status):
        errorMessage = "Error - Status code " + str(status)
        print(errorMessage)
        if status == REQUEST_LIMIT:
            print("Request limit reached. Trying again...")
            exit()

def parse_data(data):
    json_data_file = json.loads(data)
    tweetHandler = TwitterHandler()

    # Here we have to create the Queue
    
    location = json_data_file["place"]
    coordinates = json_data_file["coordinates"]
    language = json_data_file["lang"]

    # if language is "en":
    if coordinates is not None:
        # print(json_data_file["coordinates"])
        final_longitude = json_data_file["coordinates"][0]
        final_latitude = json_data_file["coordinates"][0]
    elif location is not None:
        coord_array = json_data_file["place"]["bounding_box"]["coordinates"][0]
        longitude = 0;
        latitude = 0;
        for object in coord_array:
            # print(object)
            longitude = longitude + object[0]
            latitude = latitude + object[1]
        # print(longitude / len(coord_array))
        # print(latitude / len(coord_array))

        final_longitude = longitude / len(coord_array)
        final_latitude = latitude / len(coord_array)
    #print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    # print json_data_file
    # print (type(json_data_file)

    tweetId = json_data_file['id_str']
    tweet = json_data_file["text"]
    author = json_data_file["user"]["name"]
    timestamp = json_data_file["created_at"]

    location_data = [final_longitude, final_latitude]

    try:
        # print(tweetHandler.insertTweet(tweetId, location_data, tweet, author, timestamp))

        # Format tweet into correct message format for SQS
        formatted_tweet = tweetHandler.formatTweet(tweetId, location_data, tweet, author, timestamp)
        tweet = json.dumps(formatted_tweet)
        # print(tweet)
        queue_name = sqs_queue.getQueueName('twitterTrends')
        # queue_name2 = sqs.get_queue_by_name(QueueName='twitterTrends')
        # print(queue_name)
        # print(queue_name2)
        # print(type(queue_name))
        # print(type(queue_name2))
        response = queue_name.send_message(MessageBody=tweet)
        # response = sqs_queue.sendMessage(queue_name, tweet)
        # print(type(response))
        print("Added tweet to SQS")
    except:
        print("Failed to insert tweet into SQS")
        traceback.print_exc()

def startStream():

    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessSecret)
    while True:
        try:
            twitterStream = Stream(auth, TweetListener())
            twitterStream.filter(languages=['en'], track=KEYWORDS)
        except:
            print("Restarting Stream")
            continue

    #The location specified above gets all tweets, we can then filter and store based on what we want
'''
def processData_old():
    print("Processing Data")
    queue_name = sqs_queue.getQueueName('twitterTrends')
    #print(queue_name.receive_messages(MessageAttributeNames=['author']))
    # print(type(queue_name))
    for message in queue_name.receive_messages(MessageAttributeNames=['author']):
        json_dict = json.loads(message.body)
        response = json.dumps(alchemy.sentiment(text=json_dict['message']), indent=2)
        print(response)
        json_dict['alchemy_response'] = response
        print(json_dict)
        sns.publish(TopicArn='arn:aws:sns:us-west-2:963145354502:tweets', Message=json.dumps({'default':json.dumps(json_dict)}), MessageStructure='json')
        #print("!@#$%^&*(*&^%$#@!@#$%^&*(*&^%$#@!@#$%^&*((*&^%$#@!")
        message.delete()
        # time.sleep(10)
'''
def processData():
    queue_name = sqs_queue.getQueueName('twitterTrends')
    for message in queue_name.receive_messages(MessageAttributeNames=['author']):
        json_dict = json.loads(message.body)
        response = alchemy.sentiment(text=json_dict['message'])
        json_dict['alchemy_response'] = response['docSentiment']
        # print(json_dict['alchemy_response'])
        sns.publish(TopicArn='arn:aws:sns:us-west-2:963145354502:tweets', Message=json.dumps({'default':json.dumps(json_dict)}), MessageStructure='json')
        print("!@#$%^&*(*&^%$#@!@#$%^&*(*&^%$#@!@#$%^&*((*&^%$#@!")
        message.delete()

# For testing purposes only
'''
if __name__ == '__main__':
    while True:
        try:
            startStream()
        except:
            print("Print restart")
            continue
'''
