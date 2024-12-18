import logging
import os
import boto3
from datetime import datetime, timezone
logger = logging.getLogger(__name__)

class DynamoDBRateLimiter:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DynamoDBRateLimiter, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        session = boto3.Session(
                region_name= os.environ['AWS_REGION'],
                aws_access_key_id= os.environ['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key= os.environ['AWS_SECRET_ACCESS_KEY'],
                )
        self.dynamodb = session.client('dynamodb')
        self.table_name = "RateLimit"

    def is_allowed(self, api_name, max_requests_minute):
        current_time = datetime.now(timezone.utc)
        window_start = current_time.replace(
            minute=current_time.minute, # Minute granularity only
            second=0,
            microsecond=0
        )
        timestamp_str = window_start.isoformat()
        """
        type RateLimitEntry struct {
            RateTimeKeyBucket string // Represent granularity API_NAME:<date>:minute or some other granularity
            RequestCount      int64
            MaxRequests       int64
            TTL               int64 // epoch seconds
        }
        """
        bucket_key = api_name + ":" + timestamp_str
        twoHours = 7200
       
        ttl = int(current_time.timestamp()) + twoHours
        try:
            response = self.dynamodb.update_item(
                TableName=self.table_name,
                Key={'RateTimeKeyBucket': {'S': bucket_key}},
                UpdateExpression='ADD RequestCount :incr SET MaxRequests = :mr, #timeToLive = :tl',
                ExpressionAttributeValues={':incr': {'N': '1'},
                                           ':mr': {'N': str(max_requests_minute)},
                                           ':tl': {'N': str(ttl)}
                                           },
                ReturnValues='ALL_NEW',
                ExpressionAttributeNames={
                    "#timeToLive": "TTL"
                }
            )
            request_count = int(response['Attributes']['RequestCount']['N'])
            max_requests = int(response['Attributes']['MaxRequests']['N'])
            return request_count <= max_requests
        except self.dynamodb.exceptions.ConditionalCheckFailedException:
            return False # Rate limit exceeded
        except Exception as e:
            logger.error(f"Error: {e}")
            return False