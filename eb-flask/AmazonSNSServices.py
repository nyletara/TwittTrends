import boto3

class SNSServices():
	"""docstring for SNSServices"""

	def __init__(self):
		print('Initializing SNS Service')
		self.sns = boto3.client('sns')

	def createTopic(self, topic):
		return self.sns.create_topic(Name=topic)
		
	def subscribeToSNS(self, topic, serviceEndpoint):
		return topic.subscribe(Protocol='http', Endpoint=serviceEndpoint)
