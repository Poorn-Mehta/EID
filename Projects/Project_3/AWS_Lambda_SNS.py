from __future__ import print_function
  
import json
import boto3

Set_to_Celsius = 0
Set_to_Fahrenheit = 1
  
print('Loading function')

# Ref: https://stackoverflow.com/questions/4528099/convert-string-to-json-using-python
  
def lambda_handler(event, context):
  
    # Parse the JSON message 
    Event_JSON = json.dumps(event)
    Received_JSON = json.loads(Event_JSON)
    if(Received_JSON['Type'] == 'ALERT'):
        
        Temp_txt = "\nTemperature: " + str(Received_JSON['Curr_Temp'])
        Humi_txt = "\nHumidity: " + str(Received_JSON['Curr_Humi'])
        
        if(Received_JSON['Temp_Unit'] == Set_to_Fahrenheit):
            Temp_txt += "F"
        else:
            Temp_txt += "C"
            
        Final_txt = "!!!HIGH ALERT!!!" + Temp_txt + Humi_txt + "\nAlert Levels Below"
        Final_txt += "\nTH: " + str(Received_JSON['Temp_Alert_High'])
        Final_txt += "\nTL: " + str(Received_JSON['Temp_Alert_Low'])
        Final_txt += "\nHH: " + str(Received_JSON['Humi_Alert_High'])
        Final_txt += "\nHL: " + str(Received_JSON['Humi_Alert_Low'])
  
    # Print the parsed JSON message to the console; you can view this text in the Monitoring tab in the Lambda console or in the CloudWatch Logs console
    print('Received event: ', Event_JSON)
  
    # Create an SNS client
    # ref: https://russell.ballestrini.net/setting-region-programmatically-in-boto3/
    sns = boto3.client('sns', region_name='us-east-1')
  
    # Publish a message to the specified topic
    response = sns.publish (
        TopicArn = 'arn:aws:sns:us-east-1:310687527958:EID_SNS_Proj3',
        Message = Final_txt
    )
    print(response)

