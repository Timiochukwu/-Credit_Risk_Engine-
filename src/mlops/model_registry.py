"""
Model Registry

Centralized model versioning and management
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
import pickle
import os


class ModelRegistry:
    """
    Centralized model registry
    
    Features:
    - Model versioning
    - Metadata tracking
    - Production/staging tags
    - Performance history
    - Rollback capability
    """
    
    def __init__(self, registry_path: str = "models/registry"):
        self.registry_path = registry_path
        self.models: Dict = {}
        os.makedirs(registry_path, exist_ok=True)
        self.load_registry()
    
    def register_model(self, model_name: str, version: str, metadata: Dict) -> Dict:
        """Register a new model version"""
        model_id = f"{model_name}:{version}"
        
        registration = {
            'model_id': model_id,
            'model_name': model_name,
            'version': version,
            'registered_at': datetime.now().isoformat(),
            'metadata': metadata,
            'stage': 'staging',
            'performance': metadata.get('metrics', {})
        }
        
        if model_name not in self.models:
            self.models[model_name] = {}
        
        self.models[model_name][version] = registration
        self.save_registry()
        
        return registration
    
    def promote_to_production(self, model_name: str, version: str) -> Dict:
        """Promote model to production"""
        if model_name not in self.models or version not in self.models[model_name]:
            return {'status': 'error', 'message': 'Model version not found'}
        
        # Demote current production model
        for v, model in self.models[model_name].items():
            if model['stage'] == 'production':
                model['stage'] = 'archived'
                model['archived_at'] = datetime.now().isoformat()
        
        # Promote new model
        self.models[model_name][version]['stage'] = 'production'
        self.models[model_name][version]['promoted_at'] = datetime.now().isoformat()
        self.save_registry()
        
        return {
            'status': 'success',
            'message': f'{model_name}:{version} promoted to production'
        }
    
    def get_production_model(self, model_name: str) -> Optional[Dict]:
        """Get current production model"""
        if model_name not in self.models:
            return None
        
        for version, model in self.models[model_name].items():
            if model['stage'] == 'production':
                return model
        
        return None
    
    def save_registry(self):
        """Save registry to disk"""
        with open(f"{self.registry_path}/registry.json", 'w') as f:
            json.dump(self.models, f, indent=2, default=str)
    
    def load_registry(self):
        """Load registry from disk"""
        registry_file = f"{self.registry_path}/registry.json"
        if os.path.exists(registry_file):
            with open(registry_file, 'r') as f:
                self.models = json.load(f)


if __name__ == "__main__":
    registry = ModelRegistry()
    
    # Register model
    result = registry.register_model(
        model_name='credit_risk_xgboost',
        version='1.0.0',
        metadata={
            'metrics': {'auc_roc': 0.85, 'accuracy': 0.82},
            'training_date': '2024-03-15',
            'features': 50
        }
    )
    print(json.dumps(result, indent=2, default=str))
