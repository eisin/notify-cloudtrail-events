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
    ignore_event_names = 'PutEvaluations'.split(",")

    startdatetime = datetime.datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)
    enddatetime = startdatetime + datetime.timedelta(days=1)

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
    for event_obj in event_list:
        print event_obj.display(event_old)
        event_old = event_obj

    return 0
