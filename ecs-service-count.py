#!/usr/bin/env python3
import time
import logging
import boto3
import os
import requests


def ecs_get_metadata(uri='http://172.17.0.1:51678/v1/metadata'):
	return requests.get(uri)

def ecs_get_identity(uri='http://169.254.169.254/latest/dynamic/instance-identity/document'):
	return requests.get(uri)

def ecs_service_update(cluster, service, region):

	if not region:
		ecs = boto3.setup_default_session(region_name=ecs_get_identity().get('region'))

	ecs = boto3.client('ecs')

	cluster_response = ecs.describe_clusters(
	    clusters=[cluster]
	)['clusters'][0]

	instance_count = cluster_response.get('registeredContainerInstancesCount')

	if not instance_count:
		logging.error("Could Not Get Instance Count")
		return False

	logging.info("Instance Count: {}".format(instance_count))

	service_response = ecs.describe_services(
	    cluster=cluster,
	    services=[service]
	)['services'][0]

	service_desired = service_response.get('desiredCount')
	
	if not service_desired:
		logging.error("Could Not Get Service Count")
		return False

	logging.info("Service Count: {}".format(service_desired))

	if service_desired != instance_count:
		logging.info("Updating Service Count to: {}".format(instance_count))
		ecs.update_service(
	    	cluster=cluster,
	    	service=service,
	    	desiredCount=instance_count
		)

	return True


if __name__ == "__main__":

	log_level = os.getenv('LOG_LEVEL', "INFO")

	logging.basicConfig(level=log_level)

	daemon = os.getenv('DAEMON', True)
	interval = os.getenv('INTERVAL', 30)
	region = os.getenv('AWS_DEFAULT_REGION', None)
	
	# if CLUSTER not provided get own cluster from metadata
	cluster = os.getenv('CLUSTER', None) or ecs_get_metadata().get('Cluster')
	service = os.getenv('SERVICE', None)

	if daemon:
		while True:
			ecs_service_update(cluster, service, region)
			time.sleep(interval)
	else:
		ecs_service_update(cluster, service, region)