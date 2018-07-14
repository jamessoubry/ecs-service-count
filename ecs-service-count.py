#!/usr/bin/env python3
import time
import logging
import boto3
import os
import requests


class ECSServiceUpdate(object):

    def __init__(self, cluster, service, region):

        if not region:
            boto3.setup_default_session(
                region_name=self._identity().get('region')
            )

        self.service = service
        self.cluster = cluster or self._metadata().get('Cluster')
        self.ecs = boto3.client('ecs')

    def _metadata(
        self,
        uri='http://172.17.0.1:51678/v1/metadata'
    ):
        return requests.get(uri).json()

    def _identity(
        self,
        uri='http://169.254.169.254/latest/dynamic/instance-identity/document'
    ):
        return requests.get(uri).json()

    def _cluster_response(self):
        return self.ecs.describe_clusters(
            clusters=[self.cluster]
        )['clusters'][0]

    def _service_response(self):
        return self.ecs.describe_services(
            cluster=self.cluster,
            services=[self.service]
        )['services'][0]

    def update_service(self):

        instance_count = self._cluster_response().get(
            'registeredContainerInstancesCount'
        )

        if not instance_count:
            logging.error("Could Not Get Instance Count")
            return False

        logging.info("Instance Count: {}".format(instance_count))

        service_desired = self._service_response().get('desiredCount')

        if not service_desired:
            logging.error("Could Not Get Service Count")
            return False

        logging.info(
            "Service Count: {}".format(service_desired)
        )

        if service_desired != instance_count:
            logging.info(
                "Updating Service Count to: {}".format(instance_count)
            )
            self.ecs.update_service(
                cluster=self.cluster,
                service=self.service,
                desiredCount=instance_count
            )

        return True


if __name__ == "__main__":

    log_level = os.getenv('LOG_LEVEL', "INFO")

    logging.basicConfig(level=log_level)

    daemon = os.getenv('DAEMON', True)
    interval = os.getenv('INTERVAL', 30)
    region = os.getenv('AWS_DEFAULT_REGION', None)
    cluster = os.getenv('CLUSTER', None)
    service = os.getenv('SERVICE', None)

    ecs_service_update = ECSServiceUpdate(cluster, service, region)

    if daemon:
        logging.info("Running in Daemon mode")
        while True:
            ecs_service_update.update_service()
            time.sleep(interval)
    else:
        ecs_service_update.update_service()
