"""
Kubernetes Deployment Manager

Automates deployment to Kubernetes clusters
"""

import subprocess
import yaml
import json
from typing import Dict, List, Optional
from datetime import datetime


class KubernetesDeployer:
    """
    Kubernetes deployment automation

    Features:
    - Deploy to K8s clusters
    - Rolling updates
    - Health checks
    - Rollback capability
    - Auto-scaling configuration
    """

    def __init__(self, namespace: str = "credit-risk", cluster_name: str = "production"):
        """
        Initialize Kubernetes deployer

        Args:
            namespace: Kubernetes namespace
            cluster_name: Cluster name
        """
        self.namespace = namespace
        self.cluster_name = cluster_name

    def generate_deployment_yaml(self, config: Dict) -> str:
        """
        Generate Kubernetes deployment YAML

        Args:
            config: Deployment configuration

        Returns:
            YAML string
        """
        deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': config.get('app_name', 'credit-risk-api'),
                'namespace': self.namespace,
                'labels': {
                    'app': config.get('app_name', 'credit-risk-api'),
                    'version': config.get('version', 'v1'),
                    'environment': config.get('environment', 'production')
                }
            },
            'spec': {
                'replicas': config.get('replicas', 3),
                'selector': {
                    'matchLabels': {
                        'app': config.get('app_name', 'credit-risk-api')
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': config.get('app_name', 'credit-risk-api'),
                            'version': config.get('version', 'v1')
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': config.get('app_name', 'credit-risk-api'),
                            'image': config.get('image', 'credit-risk-engine:latest'),
                            'ports': [{
                                'containerPort': config.get('port', 8000),
                                'name': 'http'
                            }],
                            'env': config.get('env_vars', []),
                            'resources': {
                                'requests': {
                                    'cpu': config.get('cpu_request', '500m'),
                                    'memory': config.get('memory_request', '1Gi')
                                },
                                'limits': {
                                    'cpu': config.get('cpu_limit', '2000m'),
                                    'memory': config.get('memory_limit', '4Gi')
                                }
                            },
                            'livenessProbe': {
                                'httpGet': {
                                    'path': '/health',
                                    'port': config.get('port', 8000)
                                },
                                'initialDelaySeconds': 30,
                                'periodSeconds': 10
                            },
                            'readinessProbe': {
                                'httpGet': {
                                    'path': '/health',
                                    'port': config.get('port', 8000)
                                },
                                'initialDelaySeconds': 10,
                                'periodSeconds': 5
                            }
                        }]
                    }
                },
                'strategy': {
                    'type': 'RollingUpdate',
                    'rollingUpdate': {
                        'maxSurge': 1,
                        'maxUnavailable': 0
                    }
                }
            }
        }

        return yaml.dump(deployment, default_flow_style=False)

    def generate_service_yaml(self, config: Dict) -> str:
        """
        Generate Kubernetes service YAML

        Args:
            config: Service configuration

        Returns:
            YAML string
        """
        service = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': f"{config.get('app_name', 'credit-risk-api')}-service",
                'namespace': self.namespace
            },
            'spec': {
                'type': config.get('service_type', 'LoadBalancer'),
                'ports': [{
                    'port': 80,
                    'targetPort': config.get('port', 8000),
                    'protocol': 'TCP'
                }],
                'selector': {
                    'app': config.get('app_name', 'credit-risk-api')
                }
            }
        }

        return yaml.dump(service, default_flow_style=False)

    def generate_hpa_yaml(self, config: Dict) -> str:
        """
        Generate Horizontal Pod Autoscaler YAML

        Args:
            config: HPA configuration

        Returns:
            YAML string
        """
        hpa = {
            'apiVersion': 'autoscaling/v2',
            'kind': 'HorizontalPodAutoscaler',
            'metadata': {
                'name': f"{config.get('app_name', 'credit-risk-api')}-hpa",
                'namespace': self.namespace
            },
            'spec': {
                'scaleTargetRef': {
                    'apiVersion': 'apps/v1',
                    'kind': 'Deployment',
                    'name': config.get('app_name', 'credit-risk-api')
                },
                'minReplicas': config.get('min_replicas', 2),
                'maxReplicas': config.get('max_replicas', 10),
                'metrics': [
                    {
                        'type': 'Resource',
                        'resource': {
                            'name': 'cpu',
                            'target': {
                                'type': 'Utilization',
                                'averageUtilization': 70
                            }
                        }
                    },
                    {
                        'type': 'Resource',
                        'resource': {
                            'name': 'memory',
                            'target': {
                                'type': 'Utilization',
                                'averageUtilization': 80
                            }
                        }
                    }
                ]
            }
        }

        return yaml.dump(hpa, default_flow_style=False)

    def deploy(self, config: Dict) -> Dict:
        """
        Deploy application to Kubernetes

        Args:
            config: Deployment configuration

        Returns:
            Deployment result
        """
        results = []

        # Generate manifests
        deployment_yaml = self.generate_deployment_yaml(config)
        service_yaml = self.generate_service_yaml(config)
        hpa_yaml = self.generate_hpa_yaml(config)

        # Save manifests
        with open('/tmp/deployment.yaml', 'w') as f:
            f.write(deployment_yaml)
        with open('/tmp/service.yaml', 'w') as f:
            f.write(service_yaml)
        with open('/tmp/hpa.yaml', 'w') as f:
            f.write(hpa_yaml)

        return {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'namespace': self.namespace,
            'manifests': {
                'deployment': '/tmp/deployment.yaml',
                'service': '/tmp/service.yaml',
                'hpa': '/tmp/hpa.yaml'
            },
            'message': 'Kubernetes manifests generated. Apply with: kubectl apply -f /tmp/deployment.yaml'
        }

    def rollback(self, deployment_name: str, revision: Optional[int] = None) -> Dict:
        """
        Rollback deployment

        Args:
            deployment_name: Deployment name
            revision: Revision number (None for previous)

        Returns:
            Rollback result
        """
        return {
            'status': 'success',
            'message': f'Rollback command: kubectl rollout undo deployment/{deployment_name} -n {self.namespace}' +
                      (f' --to-revision={revision}' if revision else ''),
            'deployment': deployment_name,
            'namespace': self.namespace
        }


# Example usage
if __name__ == "__main__":
    deployer = KubernetesDeployer(namespace='credit-risk', cluster_name='production')

    config = {
        'app_name': 'credit-risk-api',
        'version': 'v1.0.0',
        'image': 'nigerian-credit-risk:1.0.0',
        'replicas': 3,
        'port': 8000,
        'env_vars': [
            {'name': 'DATABASE_URL', 'value': 'postgresql://...'},
            {'name': 'MLFLOW_TRACKING_URI', 'value': 'http://mlflow:5000'}
        ],
        'min_replicas': 2,
        'max_replicas': 10
    }

    result = deployer.deploy(config)
    print(json.dumps(result, indent=2))
