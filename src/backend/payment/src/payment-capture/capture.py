import os
import json

from aws_lambda_powertools import Logger, Metrics

logger = Logger()
metrics = Metrics()

@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event, context):
    logger.info(event)
    
    body = json.loads(event['body'])
    
    receipt_url = "/v1/charges/"+body['chargeId']+"/refunds"
    
    json_data = {
        "capturedCharge": {
            "receipt_url": receipt_url,
            "object": "charge",
            "amount": 0
        }
    }
    
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": '*',
            "Access-Control-Allow-Methods": '*'
            },
        'body': json.dumps(json_data)   
    }
