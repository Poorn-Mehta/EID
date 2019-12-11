# Author: Poorn Mehta and Rushi Macwan
# The code was developed based on multiple AWS tutorials found online
# References Below
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs-examples.html
# https://docs.aws.amazon.com/lambda/latest/dg/with-sns-example.html
# https://docs.aws.amazon.com/lambda/latest/dg/with-sns-example.html
# https://www.alienvault.com/documentation/usm-anywhere/deployment-guide/notifications/setup-sns-topic.htm
# https://mkdev.me/en/posts/how-to-send-sms-messages-with-aws-lambda-sns-and-python-3
# https://stackoverflow.com/questions/4528099/convert-string-to-json-using-python
# https://russell.ballestrini.net/setting-region-programmatically-in-boto3/

# Imports
from __future__ import print_function
import json
import boto3

# AWS Message Types
AWS_CLR_Type_Str = "CLR"
AWS_ALT_Type_Str = "ALT"
AWS_LOW_Type_Str = "LOW"
AWS_WEB_Type_Str = "AWS"
  
print('Loading function')

# Ref: https://stackoverflow.com/questions/4528099/convert-string-to-json-using-python

# Create an SNS client
# ref: https://russell.ballestrini.net/setting-region-programmatically-in-boto3/
sns = boto3.client('sns', region_name='us-east-1')

# Create SQS client
sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-2.amazonaws.com/310687527958/EID_Proj3'

# Lambda Event Handler
def lambda_handler(event, context):
  
    # Parse the JSON message 
    Event_JSON = json.dumps(event)
    Received_JSON = json.loads(Event_JSON)
    
    if(Received_JSON['Type'] == AWS_WEB_Type_Str):
        
        print("Got AWS String")
        
        Mon_Txt = str(Received_JSON['MONST']) + str(Received_JSON['MONET'])
        Tue_Txt = str(Received_JSON['TUEST']) + str(Received_JSON['TUEET'])
        Wed_Txt = str(Received_JSON['WEDST']) + str(Received_JSON['WEDET'])
        Thu_Txt = str(Received_JSON['THUST']) + str(Received_JSON['THUET'])
        Fri_Txt = str(Received_JSON['FRIST']) + str(Received_JSON['FRIET'])
        Sat_Txt = str(Received_JSON['SATST']) + str(Received_JSON['SATET'])
        Sun_Txt = str(Received_JSON['SUNST']) + str(Received_JSON['SUNET'])
        
        response = sqs.send_message (
            QueueUrl = queue_url,
            DelaySeconds = 0,
            MessageAttributes = {
                'MON': {
                    'DataType': 'String',
                    'StringValue': Mon_Txt
                },
                'TUE': {
                    'DataType': 'String',
                    'StringValue': Tue_Txt
                },
                'WED': {
                    'DataType': 'String',
                    'StringValue': Wed_Txt
                },
                'THU': {
                    'DataType': 'String',
                    'StringValue': Thu_Txt
                },
                'FRI': {
                    'DataType': 'String',
                    'StringValue': Fri_Txt
                },
                'SAT': {
                    'DataType': 'String',
                    'StringValue': Sat_Txt
                },
                'SUN': {
                    'DataType': 'String',
                    'StringValue': Sun_Txt
                },
                'Type': {
                    'DataType': 'String',
                    'StringValue': str(Received_JSON['Type'])
                },
                'Msg_ID': {
                    'DataType': 'Number',
                    'StringValue': str(Received_JSON['Msg_ID'])
                }
            },
            MessageBody=(
                'Current Schedule'
            )
        )
        
    elif((Received_JSON['Type'] == AWS_CLR_Type_Str) or (Received_JSON['Type'] == AWS_ALT_Type_Str) or (Received_JSON['Type'] == AWS_LOW_Type_Str)):
        
        response = sqs.send_message (
            QueueUrl = queue_url,
            DelaySeconds = 0,
            MessageAttributes = {
                'Node': {
                    'DataType': 'Number',
                    'StringValue': str(Received_JSON['Node'])
                },
                'Type': {
                    'DataType': 'String',
                    'StringValue': str(Received_JSON['Type'])
                },
                'Msg_ID': {
                    'DataType': 'Number',
                    'StringValue': str(Received_JSON['Msg_ID'])
                }
            },
            MessageBody=(
                'Current State'
            )
        )
        
        if(Received_JSON['Type'] == AWS_ALT_Type_Str):
            
            Final_txt = "\n!!!HIGH ALERT!!!" + "\nSensor Node: " + str(Received_JSON['Node']) + " Detected a Breach"
            Final_txt += "\nTimeStamp: " + str(Received_JSON['Timestamp'])
            
            response = sns.publish (TopicArn = 'arn:aws:sns:us-east-1:310687527958:EID_SNS_Proj3', Message = Final_txt)

        elif(Received_JSON['Type'] == AWS_LOW_Type_Str):
            
            Final_txt = "\n!Important Notification!" + "\nSensor Node: " + str(Received_JSON['Node']) + " is running on Low Battery"
            Final_txt += "\nTimeStamp: " + str(Received_JSON['Timestamp'])
            
            response = sns.publish (TopicArn = 'arn:aws:sns:us-east-1:310687527958:EID_SNS_Proj3', Message = Final_txt)
            
    else:
        
        response = "\nUnsupported JSON Received"
  
    # Print the parsed JSON message to the console; you can view this text in the Monitoring tab in the Lambda console or in the CloudWatch Logs console
    print('Received event: ', Event_JSON)
  
    print(response)

