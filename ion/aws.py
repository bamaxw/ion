'''Helper classes and functions facilitating boto3 usage'''
from typing import Optional, Generator
import logging
import time
import re

import boto3

from .json import dump
from .time import msts
from .bash import colors

AWS_DEFAULT_REGION = 'eu-west-1'
log = logging.getLogger(__name__)


class AWSManager:
    '''
    Wrapper class aroung boto3 providing easier access to often required functionalities
    Arguments:
        region_name: default region name to be used by boto3
    '''
    def __init__(self, region_name: str = AWS_DEFAULT_REGION):
        self.region_name = region_name
        self._clients = {}
        self._resources = {}

    def client(self, client_name: str, region_name: Optional[str] = None):
        '''Get boto3 client equivalent to boto3.client(client_name, region_name=region_name)'''
        log.info('Creating %s client [region: %s]!', client_name, region_name or self.region_name)
        if client_name not in self._clients:
            self._clients[client_name] = boto3.client(client_name, region_name=region_name or self.region_name)
        return self._clients[client_name]

    def resource(self, resource_name: str, region_name: Optional[str] = None):
        '''Get boto3 resource equivalent to boto3.resource(resource_name, region_name=region_name)'''
        log.info('Creating %s resource [region: %s]!', resource_name, region_name or self.region_name)
        if resource_name not in self._clients:
            self._resources[resource_name] = boto3.resource(resource_name, region_name=region_name or self.region_name)
        return self._resources[resource_name]

    def get_export(self, export_name: str, **kw):
        '''Get value of CloudFormation export'''
        cloud_formation = self.client('cloudformation', **kw)
        args = {}
        while True:
            response = cloud_formation.list_exports(**args)
            for export in response.get('Exports', []):
                if export['Name'] == export_name:
                    log.warning("Export '%s': %s", export_name, export['Value'])
                    return export['Value']
            next_token = response.get('NextToken')
            if next_token is None:
                break
            args = {'NextToken': next_token}
        raise ValueError(f'Could not find export value for {export_name}')

    def stream_logs(
            self,
            log_group: str,
            stream_prefix: str,
            *,
            filter_pattern: Optional[str] = None,
            start: Optional[int] = None,
            disable_highlight: bool = False,
            **kw
    ) -> Generator[str, None, None]:
        '''
        Gets log events from aws logs stream, and yields them out in a form
        (<message>, <message with bash formatted highlight>)
        Arguments:
            log_group:       which log group should the logs be streamed from
            stream_prefix:   which log streams should be included in this stream
                             must include streams or prefix but not both!
            prefix:          streams with which prefix should be included in this streams
                             must include streams or prefix but not both!
            filter_pattern:  specify filter for the logs
            start:           when should the stream begin, by default it's the timestamp of when
                             this method was called
        '''
        logs = self.client('logs', **kw)
        params = dict(
            logGroupName=log_group,
            orderBy='LastEventTime',
            descending=True
        )
        paginator = logs.get_paginator('describe_log_streams')
        stream_iterator = paginator.paginate(**params)
        jmespath = f"logStreams[?starts_with(logStreamName, `{stream_prefix}`)]"
        filtered_iterator = stream_iterator.search(jmespath)
        try:
            stream = next(filtered_iterator)['logStreamName']
        except StopIteration:
            raise ValueError(f"Can't find log stream with prefix: {stream_prefix} in log group: {log_group}!")
        if start is None:
            start = msts()
        start_time = start
        next_token = {}
        log.info('Getting log events from %s', stream)
        while True:
            response = logs.get_log_events(
                logGroupName=log_group,
                logStreamName=stream,
                startTime=start_time,
                limit=100,
                startFromHead=True,
                **next_token
            )
            for event in response['events']:
                msg = event['msg']
                if not filter_pattern:
                    yield msg, None
                elif re.search(filter_pattern, msg):
                    if disable_highlight:
                        yield msg, None
                    else:
                        msg_highlight = re.sub(f'({filter_pattern})', fr'{colors.yellow}\1{colors.reset}', msg)
                        yield msg, msg_highlight
                else:
                    log.debug('Rejecting message: %s', event['message'])
            next_token = {'nextToken': response['nextForwardToken']}
            time.sleep(0.1)


# AWSManager with default variables is available as AWS from ion.aws
AWS = AWSManager()
