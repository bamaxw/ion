'''Helper classes and functions facilitating boto3 usage'''
from typing import Optional
import logging

import boto3

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

    def get_export(self, export_name: str):
        '''Get value of CloudFormation export'''
        cloud_formation = self.client('cloudformation')
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


# AWSManager with default variables is available as AWS from ion.aws
AWS = AWSManager()
