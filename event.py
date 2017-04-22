# -*- coding: utf-8 -*-

from datetime import datetime
from collections import OrderedDict
import boto3

class EventBase():
    def __init__(self, event, tz):
        self.tz = tz
        for key in event.keys():
            setattr(self, key, event.get(key))

    def make_header(self):
        event_datetime = self.EventTime
        if isinstance(event_datetime, float):
            event_datetime = datetime.fromtimestamp(event_datetime, self.tz)
        event_datetime = event_datetime.astimezone(self.tz)
        event_datetime_disp = event_datetime.strftime("%Y/%m/%d(%a) %H:%M").decode('utf-8')
        event_time_disp = event_datetime.strftime("%H:%M").decode('utf-8')
        return u"\n".join((
            u"■{1} {0.Username}".format(self, event_datetime_disp),
            u"  ({1}) {0.EventName}".format(self, event_time_disp),
        ))

class EventInstance(EventBase):
    def __init__(self, event, tz):
        EventBase.__init__(self, event, tz)

    def display(self):
        header = self.make_header()
        parameters = OrderedDict()
        for resource in self.Resources:
            if resource.get("ResourceType") == "AWS::EC2::Instance":
                instance_name = EventInstance.get_instance_name(resource.get("ResourceName"))
                if not instance_name is None:
                    parameters[resource.get("ResourceType")] = "{0} ({1})".format(
                        resource.get("ResourceName"), instance_name)
                continue
            parameters[resource.get("ResourceType")] = resource.get("ResourceName")
                
        output = [header]
        for param in  parameters.keys():
            output.append(u"    [{0}] {1}".format(param, parameters[param]))
        return u"\n".join(output)

    @classmethod
    def get_instance_name(cls, target_instance_id):
        instances_list = EventInstance.instances()
        for i in instances_list:
            if i.instance_id == target_instance_id:
                for tag in i.tags:
                    if tag['Key'] == 'Name':
                        return tag['Value']
        return None

    @classmethod
    def instances(cls):
        if cls._instances is None:
            cls._instances = cls.retreive_instances()
        return cls._instances
    #instances._instances = None
    _instances = None

    @classmethod
    def retreive_instances(cls):
        result = []
        ec2 = boto3.resource('ec2')
        for instance in ec2.instances.all():
            result.append(instance)
        return result
                
        

class EventOther(EventBase):
    #ignore_field = ['EventId', 'EventTime', 'tz', 'CloudTrailEvent', 'EventName', 'Username']
    ignore_field = []
    def __init__(self, event, tz):
        EventBase.__init__(self, event, tz)

    def display(self):
        header = self.make_header()
        #return header
        #event_dict = vars(self)
        output = [header]
        for resource_dict in self.Resources:
            if resource_dict.get('ResourceType') in self.ignore_field:
                continue
            output.append(u"    [{0}] {1}".format(resource_dict.get('ResourceType'), resource_dict.get('ResourceName')))
        return u"\n".join(output)
