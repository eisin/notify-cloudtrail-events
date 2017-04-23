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

import event

def handler(lambda_event, lambda_context):
    tz = pytz.timezone('Asia/Tokyo')
    locale.setlocale(locale.LC_ALL, 'ja_JP.utf-8')
    ignore_event_names = 'ConsoleLogin,PutEvaluations,CreateLogStream'.split(",")
    sns_arn = 'arn:aws:sns:ap-northeast-1:626676598765:notify-aws-service'
    sns_subject = u"[AWS]CloudTrail report"

    #startdatetime = datetime.datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)
    #enddatetime = startdatetime + datetime.timedelta(days=1)
    startdatetime = datetime.datetime.now(tz).replace(minute=0, second=0, microsecond=0) - datetime.timedelta(hours=1)
    enddatetime = startdatetime + datetime.timedelta(hours=1)

    cloudtrail = boto3.client('cloudtrail')
    event_list = []

    logs = cloudtrail.lookup_events(StartTime=startdatetime, EndTime=enddatetime)
    event_result = logs.get("Events")
    while len(event_result) > 0:
        for event_dict in event_result:
            event_obj = event.Event(event_dict, tz)

            if event_obj.EventName in ignore_event_names:
                continue
            event_list.append(event_obj)
    
        if logs.get("NextToken"):
            logs = cloudtrail.lookup_events(NextToken=logs.get("NextToken"))
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
