# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(__file__))

import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

import boto3
import json

import datetime
import pytz
import locale
import fnmatch

import event

def handler(lambda_event, lambda_context):
    tz = pytz.timezone(os.environ.get('tz', 'Asia/Tokyo'))
    locale.setlocale(locale.LC_ALL, os.environ.get('ja_JP.utf-8'))
    ignore_event_names = os.environ.get('ignore_event_names', '').split(":")
    ignore_event_names += ["List*", "Describe*", "Get*", "CheckMfa", "Decrypt", "Lookup*", "PutEvaluations", "CreateLogStream", "AssumeRole", "Discover*", "Submit*StateChange", "Discover*", "SwitchRole", "BatchGet*"]
    ignore_user_names = os.environ.get('ignore_user_names', '').split(":")
    ignore_user_names += ["ecs-eni-provisioning"]
    sns_arn = os.environ.get('sns_arn', '')
    sns_subject = os.environ.get('sns_subject', '')
    target_duration = os.environ.get('target_duration', '1hour') # 1hour or 1day

    if target_duration == "1hour":
        startdatetime = datetime.datetime.now(tz).replace(minute=0, second=0, microsecond=0) - datetime.timedelta(hours=1)
        enddatetime = startdatetime + datetime.timedelta(hours=1)
    elif target_duration == "1day":
        startdatetime = datetime.datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)
        enddatetime = startdatetime + datetime.timedelta(days=1)
    else:
        return 2

    cloudtrail = boto3.client('cloudtrail')
    event_list = []

    logs = cloudtrail.lookup_events(StartTime=startdatetime, EndTime=enddatetime, LookupAttributes=[{'AttributeKey': 'ReadOnly', 'AttributeValue': 'false'},],)
    event_result = logs.get("Events")
    while len(event_result) > 0:
        for event_dict in event_result:
            event_obj = event.Event(event_dict, tz)

            event_name = event_obj.EventName
            if event_name is None:
                event_name = ""
            user_name = event_obj.Username
            if user_name is None:
                user_name = ""
            matched = False
            for ignore_event_name in ignore_event_names:
                if fnmatch.fnmatch(event_name, ignore_event_name):
                    matched = True
                    continue
            for ignore_user_name in ignore_user_names:
                if fnmatch.fnmatch(user_name, ignore_user_name):
                    matched = True
                    continue

            if not matched:
                event_list.append(event_obj)
    
        if logs.get("NextToken"):
            logs = cloudtrail.lookup_events(NextToken=logs.get("NextToken"), StartTime=startdatetime, EndTime=enddatetime, LookupAttributes=[{'AttributeKey': 'ReadOnly', 'AttributeValue': 'false'},],)
            event_result = logs.get("Events")
        else:
            break

    event_list.reverse()
    event_old = None
    output = ""
    for event_obj in event_list:
        output += event_obj.display(event_old)
        output += "\n"
        event_old = event_obj

    if output == "":
        return 1

    sns = boto3.client('sns')
    sns.publish(
        TopicArn=sns_arn,
        Message=output,
        Subject=sns_subject,
    )

    return 0
