# notify-cloudtrail-events

This lambda function is intended to be called repeatedly, it checks recent CloudTrail events and sends summary text to SNS.

### Environments

- ```target_duration```: Trigger cycle ```1hour``` or ```1day``` (default/ ```1hour```)
- ```tz```: Time zone (using pytz, default: ```Asia/Tokyo```)
- ```locale```: Locale (default: ```ja_JP.utf-8```)
- ```sns_arn```: SNS ARN
- ```sns_subject```: Message Subject
- ```ignore_event_names```: Event names to ignore (default: none, recommended: ```CreateNetworkInterface:DeleteNetworkInterface```)
- ```ignore_user_names```: Users to ignore (default: none)

This function ignores following events implicitly:
```"List*", "Describe*", "Get*", "CheckMfa", "Decrypt", "Lookup*", "PutEvaluations", "CreateLogStream"```

### Example Output

```
■2000/00/00(XXX) 00:00 by USERNAME
  (00:00) StartInstances
          - [EC2 Instance] i-00000000000000000
            <Name> INSTANCENAME
  (00:00) RunInstances
          - [EC2 Instance] i-00000000000000000
            <Name> INSTANCENAME
          - [EC2 Ami] Amazon Linux AMI 2017.03.1.20170812 x86_64 HVM GP2 (ami-00000000)
  (00:00) CreateSecurityGroup
  (00:00) AuthorizeSecurityGroupIngress

■2000/00/00(XXX) 00:00 by USERNAME
  (00:00) CreateFunction20150331
          - [Lambda Function] FUNCNAME
  (00:00) UpdateFunctionConfiguration20150331v2
          - [Lambda Function] FUNCNAME
```

## License

Apache License 2.0
