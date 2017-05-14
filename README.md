# notify-cloudtrail-events

This lambda function is intended to be called repeatedly, it checks recent CloudTrail events and sends to SNS. 

### Environments

- ```target_duration```: Trigger cycle ```1hour``` or ```1day``` (default/ ```1hour```)
- ```tz```: Time zone (using pytz, default: ```Asia/Tokyo```)
- ```locale```: Locale (default: ```ja_JP.utf-8```)
- ```sns_arn```: SNS ARN
- ```sns_subject```: Message Subject
- ```ignore_event_names```: Event names to ignore (default: none, recommended: ```ConsoleLogin:PutEvaluations:CreateLogStream:CreateNetworkInterface:DeleteNetworkInterface:ChangePassword```)
- ```ignore_user_names```: Users to ignore (default: none)


