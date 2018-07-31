# -*- coding: utf-8 -*-

from datetime import datetime
import datetime
from collections import OrderedDict
import boto3
import re

class Event():
    ignore_resourcetypes = [
        "AWS::EC2::KeyPair",
        "AWS::EC2::VPC",
        "AWS::EC2::Subnet",
        "AWS::EC2::NetworkInterface",
        "AWS::EC2::SecurityGroup",
    ]
    def __init__(self, event, tz):
        self.tz = tz
        self.EventId = None
        self.EventName = None
        self.Username = None
        self.ResourceType = None
        self.ResourceName = None
        self.EventSource = None
        for key in event.keys():
            setattr(self, key, event.get(key))
        if isinstance(self.EventTime, float):
            self.EventTime = datetime.fromtimestamp(self.EventTime, self.tz)
        self.EventTime = self.EventTime.astimezone(self.tz)

    def make_header(self):
        event_datetime_disp = self.EventTime.strftime("%Y/%m/%d(%a) %H:%M").decode('utf-8')
        event_time_disp = self.EventTime.strftime("%H:%M").decode('utf-8')
        return u"■{1} by {0.Username}".format(self, event_datetime_disp)

    def make_event_line(self):
        event_datetime_disp = self.EventTime.strftime("%Y/%m/%d(%a) %H:%M").decode('utf-8')
        event_time_disp = self.EventTime.strftime("%H:%M").decode('utf-8')
        return u"  ({1}) {0.EventName}".format(self, event_time_disp)

    def make_event_parameters(self):
        result = []
        for resource_dict in self.Resources:
            result_local = []
            resourcetype = resource_dict.get('ResourceType', "")
            resourcetype_disp = resourcetype
            resourcetype_disp = resourcetype.replace("AWS::", "")
            resourcetype_disp = resourcetype_disp.replace("::", " ")
            resourcename = resource_dict.get('ResourceName', "")
            description = None
            if resourcetype in self.ignore_resourcetypes:
                continue
            if resourcetype == "AWS::EC2::Instance":
                tags_dict = Event.get_instance_tags(resourcename)
                if tags_dict:
                    for key, value in tags_dict.iteritems():
                        result_local.append(u"            <{0}> {1}".format(key, value))
            if resourcetype == "" and re.match(r"^i-[0-9a-z]+$", resourcename):
                tags_dict = Event.get_instance_tags(resourcename)
                if tags_dict:
                    for key, value in tags_dict.iteritems():
                        result_local.append(u"            <{0}> {1}".format(key, value))
            if resourcetype == "AWS::EC2::Ami":
                image = Event.retreive_image_by_image_id(resourcename)
                description = image.description
            if resourcetype_disp != "":
                resourcetype_disp = "[{0}] ".format(resourcetype_disp)
            if description is None:
                result.append(u"          - {0}{1}".format(resourcetype_disp, resourcename))
            else:
                result.append(u"          - {0}{2} ({1})".format(resourcetype_disp, resourcename, description))
            result.extend(result_local)
        return result

    def display(self, before_event = None):
        header = self.make_header()
        output = []
        header_skip = False
        if not before_event is None:
            delta = self.EventTime - before_event.EventTime
            if self.Username == before_event.Username and delta < datetime.timedelta(hours=1):
                header_skip = True
        if not header_skip:
            output.append(self.make_header())
        output.append(self.make_event_line())
        output.extend(self.make_event_parameters())
        return u"\n".join(output)

    @classmethod
    def get_instance_name(cls, target_instance_id):
        instances_list = Event.instances()
        for i in instances_list:
            if i.instance_id == target_instance_id:
                for tag in i.tags:
                    if tag['Key'] == 'Name':
                        return tag['Value']
        return None

    @classmethod
    def get_instance_tags(cls, target_instance_id):
        instances_list = Event.instances()
        tags_dict = OrderedDict()
        for i in instances_list:
            if i.instance_id == target_instance_id:
                for tag in i.tags:
                    tags_dict[tag['Key']] = tag['Value']
                return tags_dict
        return None

    @classmethod
    def instances(cls):
        if cls._instances is None:
            cls._instances = cls.retreive_instances()
        return cls._instances
    _instances = None

    @classmethod
    def retreive_instances(cls):
        result = []
        ec2 = boto3.resource('ec2')
        for instance in ec2.instances.all():
            result.append(instance)
        return result

    @classmethod
    def retreive_image_by_image_id(cls, image_id):
        result = []
        ec2 = boto3.resource('ec2')
        return ec2.Image(image_id)
