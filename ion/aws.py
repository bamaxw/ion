'''Helper classes and functions facilitating boto3 usage'''
from typing import Optional, Generator
from functools import wraps
import logging
import time

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.types import TypeDeserializer

from .time import msts

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
        if client_name not in self._clients:
            log.info('Creating %s client [region: %s]!', client_name, region_name or self.region_name)
            self._clients[client_name] = boto3.client(client_name, region_name=region_name or self.region_name)
        return self._clients[client_name]

    def resource(self, resource_name: str, region_name: Optional[str] = None):
        '''Get boto3 resource equivalent to boto3.resource(resource_name, region_name=region_name)'''
        if resource_name not in self._resources:
            log.info('Creating %s resource [region: %s]!', resource_name, region_name or self.region_name)
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

    def read_file(self, bucket: str, key: str, *, decode: bool = True) -> str:
        '''
        Get file from S3 bucket
        Arguments:
            bucket -- bucket to read the file from
            key    -- file location within the bucket
            decode -- if True return string else return bytes
        '''
        content = self.resource('s3').Object(bucket, key).get()['Body'].read()
        if decode:
            return content.decode('utf-8')
        return content

    def put_object(self, *, body: str, bucket: str, key: str, **kw):
        '''Create or update file in S3'''
        try:
            body = body.encode('utf-8')
        except AttributeError:
            pass
        return self.client('s3').put_object(Body=body, Bucket=bucket, Key=key, **kw)

    def remove_object(self, *, bucket: str, key: str, **kw):
        '''Remove object from s3'''
        return self.client('s3').delete_object(Bucket=bucket, Key=key, **kw)

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
            yield from response['events']
            next_token = {'nextToken': response['nextForwardToken']}
            time.sleep(0.1)



# AWSManager with default variables is available as AWS from ion.aws
AWS = AWSManager()

def ddb_deserialize(o: dict):
    '''
    Deserialize DDB value
    Usage:
        >>> ddb_deserialize({'N': '200'})
        Decimal('200')
    '''
    return TypeDeserializer().deserialize(o)

def retry_on(*error_codes):
    '''
    Creates a decorator function that wraps any function, and in effect, if that function
    raises a botocore's ClientError, it's error code is going to be compared with the list
    passed to the 'retry_on' function
    If the code matches at least one of the codes provided - the function is going to be retried
    '''
    error_codes = set(error_codes)
    def _retry_on_decorator(func):
        @wraps(func)
        def _wrapper(*a, **kw):
            retries = 0
            while True:
                try:
                    return func(*a, **kw)
                except ClientError as ex:
                    if ex.response['Error']['Code'] not in error_codes:
                        raise
                    time.sleep(min(2 ** retries, 10))
                    retries += 1
        return _wrapper
    return _retry_on_decorator

def ignore(*error_codes):
    '''
    Creates a decorator function that wraps any function, and in effect, if that function
    raises a botocore's ClientError, it's error code is going to be compared with the list
    passed to the 'retry_on' function
    If the code matches at least one of the codes provided - the error is going to be ignored
    and the function exits
    '''
    error_codes = set(error_codes)
    def _ignore_decorator(func):
        @wraps(func)
        def _wrapper(*a, **kw):
            try:
                return func(*a, **kw)
            except ClientError as ex:
                if ex.response['Error']['Code'] not in error_codes:
                    raise
        return _wrapper
    return _ignore_decorator
