# -*- coding: utf-8 -*-

import boto3
import json

#from event import *
import sys
import os
sys.path.append(os.path.dirname(__file__))

import datetime
import pytz
import locale

import event

def handler(event, context):
    tz = pytz.timezone('Asia/Tokyo')
    locale.setlocale(locale.LC_ALL, 'ja_JP.utf-8')

    f = open('lookup_events.txt')
    json_text = f.read()
    f.close()
    logs = json.loads(json_text)

    cloudtrail = boto3.client('cloudtrail')
    logs = cloudtrail.lookup_events()

    event_list = logs.get("Events")
    event_list.reverse()
    for event_dict in event_list:
        event = event_new(event_dict, tz)
        print event.display()
    
    return 0

def event_new(event_dict, tz):
    if event_dict.get("EventName") in ['StartInstances', 'StopInstances']:
        return event.EventInstance(event_dict, tz)
    return event.EventOther(event_dict, tz)
