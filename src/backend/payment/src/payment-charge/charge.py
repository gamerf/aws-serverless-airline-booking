import os
import json

from aws_lambda_powertools import Logger, Metrics

logger = Logger()
metrics = Metrics()

@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event, context):
    logger.info(event)

    body = json.loads(event['body'])

    stripeToken = body['stripeToken']
    chargeId = "ch_"+stripeToken.split('_')[1]

    json_data = {
        "chargeId": chargeId
    }

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": '*',
            "Access-Control-Allow-Methods": '*'
            },
        'body': json_data    
    }
