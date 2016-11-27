import tweepy
import json
import ConfigParser
from tweepy import Stream
from tweepy.streaming import StreamListener
from TweetHandler import TwitterHandler
from AmazonSQSServices import SQSServices
from ElasticSearchServices import ElasticSearchServices
from watson_developer_cloud import AlchemyLanguageV1

config = ConfigParser.ConfigParser()
config.readfp(open(r'./configurations.txt'))

consumerKey=config.get('API Keys', 'consumerKey')
consumerSecret=config.get('API Keys', 'consumerSecret')
accessToken=config.get('API Keys', 'accessToken')
accessSecret=config.get('API Keys', 'accessSecret')

KEYWORDS = ['chelsea', 'premier', 'pokemon', 'fruit', 'food', 'coffee', 'pizza', 'california']
REQUEST_LIMIT = 420

try:
    sqs_queue = SQSServices()
    sqs_queue.createQueue("twitterTrends")   
    print(sqs_queue.url)
except Exception as e:
    print("Queue twitterTrends already exists")

try:
    sns_service = SNSService()
except Exception as e:
    print("SNS service already established")

alchemy = AlchemyLanguageV1(api_key='')

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
        except:
            # print(data)
            print("No location data found")

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

    if language is "en":
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
        print(queue_name.sendMessage(tweet))
    except:
        print("Failed to insert tweet into SQS")

def startStream():

    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessSecret)
    while True:
        try:
            twitterStream = Stream(auth, TweetListener())
            twitterStream.filter(track=KEYWORDS)
        except:
            print("Restarting Stream")
            continue

    #The location specified above gets all tweets, we can then filter and store based on what we want

def processData():
    for message in sqs_queue.receiveMessage(twitterTrends, author):
        for finaltweets2 in message.body:
            print(finaltweets2)


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