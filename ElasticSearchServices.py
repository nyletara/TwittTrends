# This is the file where we connect to ES + find and insert data
import ConfigParser
from elasticsearch import Elasticsearch

config = ConfigParser.ConfigParser()
config.readfp(open(r'./configurations.txt'))

HOSTADDRESS=config.get('ES Instance', 'HOSTADDRESS')
PORT=config.get('ES Instance', 'PORT')
USERNAME=config.get('ES Instance', 'USERNAME')
PASSWORD=config.get('ES Instance', 'PASSWORD')

# index = "finaltwittermapindex2"

class ElasticSearchServices:

    def __init__(self):
        self.es = Elasticsearch(
        		[HOSTADDRESS],
        		# http_auth=(USERNAME,PASSWORD),
        		port=PORT
        	)

    def store_data(self, index, doc_type, body):
        results = self.es.index(
    			index=index, 
    			doc_type=doc_type, 
    			body=body
    		)

        return results

    def create_collection(self, index, body):
        print "Creating collection..."
        results = self.es.indices.create(
            index=index,
            body=body
        )
        return results

    def search(self, index, doc_type, body, size):
    	results = self.es.search(
    			index = index,
    			doc_type = doc_type,
    			body = body,
    			size = size
    		)

    	return results;

    def total_hits(results):
    	return results['hits']['total']

