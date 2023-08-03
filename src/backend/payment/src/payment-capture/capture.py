import os
import json

from aws_lambda_powertools import Logger, Metrics

logger = Logger()
metrics = Metrics()

@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event, context):
    logger.info(event)

    return {
        'statusCode': 200,
        'body': json.dumps('Payment capture processed!')
    
    }
