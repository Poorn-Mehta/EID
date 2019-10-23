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

# To handle temperature units
Set_to_Celsius = 0
Set_to_Fahrenheit = 1
  
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
    
    # Formatting required for relaying messages
    Time_Val_txt = str(Received_JSON['Timestamp']) 
    Temp_Val_Txt = str(Received_JSON['Curr_Temp'])
    Humi_Val_Txt = str(Received_JSON['Curr_Humi'])
    
    # Checking the message type - Alert to SNS, Data to SQS
    if(Received_JSON['Type'] == 'ALERT'):
        
        Time_Txt = "\nTimeStamp: " + Time_Val_txt
        Temp_txt = "\nTemperature: " + Temp_Val_Txt
        Humi_txt = "\nHumidity: " + Humi_Val_Txt
        
        if(Received_JSON['Temp_Unit'] == Set_to_Fahrenheit):
            Temp_txt += "F"
        else:
            Temp_txt += "C"
            
        Final_txt = "\n!!!HIGH ALERT!!!" + Time_Txt + Temp_txt + Humi_txt + "\nAlert Levels Below"
        Final_txt += "\nTH: " + str(Received_JSON['Temp_Alert_High'])
        Final_txt += "\nTL: " + str(Received_JSON['Temp_Alert_Low'])
        Final_txt += "\nHH: " + str(Received_JSON['Humi_Alert_High'])
        Final_txt += "\nHL: " + str(Received_JSON['Humi_Alert_Low'])
      
        # Publish a message to the specified topic
        response = sns.publish (TopicArn = 'arn:aws:sns:us-east-1:310687527958:EID_SNS_Proj3', Message = Final_txt)
        
    elif(Received_JSON['Type'] == 'DATA'):
        
        response = sqs.send_message (
            QueueUrl = queue_url,
            DelaySeconds = 0,
            MessageAttributes = {
                'Temperature': {
                    'DataType': 'Number',
                    'StringValue': Temp_Val_Txt
                },
                'Humidity': {
                    'DataType': 'Number',
                    'StringValue': Humi_Val_Txt
                },
                'Timestamp': {
                    'DataType': 'String',
                    'StringValue': Time_Val_txt
                },
                'Temp_Unit': {
                    'DataType': 'Number',
                    'StringValue': str(Received_JSON['Temp_Unit'])
                },
                'Msg_ID': {
                    'DataType': 'Number',
                    'StringValue': str(Received_JSON['Msg_ID'])
                }
            },
            MessageBody=(
                'DHT22 Sensor Data'
            )
        )
        
    else:
        
        response = "\nUnsupported JSON Received"
  
    # Print the parsed JSON message to the console; you can view this text in the Monitoring tab in the Lambda console or in the CloudWatch Logs console
    print('Received event: ', Event_JSON)
  
    print(response)