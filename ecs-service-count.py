#!/usr/bin/env python3
import time
import logging
import boto3
import os


def ecs_service_update(cluster, service):


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
	cluster = os.getenv('CLUSTER', 'ecosystems-vegas-ci-develop-cluster')
	service = os.getenv('SERVICE', 'ecosystems-vegas-ci-develop-cluster-mgmt-2')

	if daemon:
		while True:
			ecs_service_update(cluster, service)
			time.sleep(interval)
	else:
		ecs_service_update(cluster, service)