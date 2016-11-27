import boto3

class SQSServices():
	
	"""docstring for SQSServices"""

	def __init__(self):
		self.sqs = boto3.resource('sqs')
		return self.sqs.get_queue_by_name(QueueName=name)

	def getQueueName(self, name):
		queueName = self.sqs.get_queue_by_name(QueueName=name)
		return queueName

	def sendMessage(queueName, message):
		return queueName.send_messages(MessageBody=message)

	def receiveMessage(queueName, messageAttribute):
		return queueName.receive_messages(MessageAttributeNames=[messageAttribute])

		
		