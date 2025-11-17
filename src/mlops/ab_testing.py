"""
A/B Testing Engine

Test multiple models in production
"""

import json
import random
from typing import Dict, List
from datetime import datetime


class ABTestingEngine:
    """A/B testing for ML models"""
    
    def __init__(self):
        self.experiments: Dict = {}
        self.results: List[Dict] = []
    
    def create_experiment(self, experiment_name: str, models: List[Dict], traffic_split: List[float]) -> Dict:
        """Create A/B test experiment"""
        experiment = {
            'experiment_id': f"EXP_{datetime.now().strftime('%Y%m%d')}_{experiment_name}",
            'name': experiment_name,
            'models': models,
            'traffic_split': traffic_split,
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
        
        self.experiments[experiment['experiment_id']] = experiment
        return experiment
    
    def assign_variant(self, experiment_id: str, user_id: str) -> str:
        """Assign user to model variant"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return None
        
        # Deterministic assignment based on user_id hash
        random.seed(hash(user_id))
        variant_index = random.choices(
            range(len(experiment['models'])),
            weights=experiment['traffic_split']
        )[0]
        
        return experiment['models'][variant_index]['model_name']
    
    def record_result(self, experiment_id: str, variant: str, actual: int, predicted: float):
        """Record prediction result"""
        self.results.append({
            'experiment_id': experiment_id,
            'variant': variant,
            'actual': actual,
            'predicted': predicted,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_experiment_results(self, experiment_id: str) -> Dict:
        """Get experiment performance"""
        exp_results = [r for r in self.results if r['experiment_id'] == experiment_id]
        
        # Group by variant
        variants = {}
        for result in exp_results:
            variant = result['variant']
            if variant not in variants:
                variants[variant] = {'predictions': 0, 'correct': 0}
            
            variants[variant]['predictions'] += 1
            if (result['predicted'] > 0.5 and result['actual'] == 1) or \
               (result['predicted'] <= 0.5 and result['actual'] == 0):
                variants[variant]['correct'] += 1
        
        # Calculate accuracy
        for variant in variants:
            variants[variant]['accuracy'] = variants[variant]['correct'] / variants[variant]['predictions']
        
        return {'experiment_id': experiment_id, 'results': variants}


if __name__ == "__main__":
    engine = ABTestingEngine()
    
    # Create experiment
    exp = engine.create_experiment(
        experiment_name='xgboost_vs_lightgbm',
        models=[
            {'model_name': 'xgboost_v1', 'version': '1.0.0'},
            {'model_name': 'lightgbm_v1', 'version': '1.0.0'}
        ],
        traffic_split=[0.5, 0.5]
    )
    print(json.dumps(exp, indent=2, default=str))
