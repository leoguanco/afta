"""
SklearnPhaseClassifier - Infrastructure Layer

Scikit-learn implementation of PhaseClassifierPort.
"""
from typing import List, Optional
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import joblib
import os

from src.domain.ports.phase_classifier_port import PhaseClassifierPort
from src.domain.value_objects.game_phase import GamePhase
from src.domain.value_objects.phase_features import PhaseFeatures


class SklearnPhaseClassifier(PhaseClassifierPort):
    """
    RandomForest-based phase classifier.
    
    Uses scikit-learn's RandomForestClassifier with feature scaling.
    Supports training, inference, and model persistence.
    """
    
    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: Optional[int] = 10,
        random_state: int = 42,
        model_path: Optional[str] = None
    ):
        """
        Initialize the classifier.
        
        Args:
            n_estimators: Number of trees in the forest
            max_depth: Maximum tree depth (None for unlimited)
            random_state: Random seed for reproducibility
            model_path: Optional path to load pre-trained model
        """
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            class_weight="balanced",  # Handle class imbalance
            n_jobs=-1  # Use all CPUs
        )
        self.scaler = StandardScaler()
        self._is_trained = False
        self._label_mapping = {
            phase: idx for idx, phase in enumerate(GamePhase)
        }
        self._reverse_mapping = {
            idx: phase for phase, idx in self._label_mapping.items()
        }
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def classify(self, features: PhaseFeatures) -> GamePhase:
        """Classify a single frame."""
        if not self._is_trained:
            return GamePhase.UNKNOWN
        
        X = features.to_vector().reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        pred = self.model.predict(X_scaled)[0]
        return self._reverse_mapping.get(pred, GamePhase.UNKNOWN)
    
    def classify_batch(self, features_list: List[PhaseFeatures]) -> List[GamePhase]:
        """Classify multiple frames in batch."""
        if not self._is_trained or not features_list:
            return [GamePhase.UNKNOWN] * len(features_list)
        
        X = np.array([f.to_vector() for f in features_list])
        X_scaled = self.scaler.transform(X)
        preds = self.model.predict(X_scaled)
        return [self._reverse_mapping.get(p, GamePhase.UNKNOWN) for p in preds]
    
    def classify_with_confidence(
        self, features: PhaseFeatures
    ) -> tuple[GamePhase, float]:
        """Classify with confidence score."""
        if not self._is_trained:
            return GamePhase.UNKNOWN, 0.0
        
        X = features.to_vector().reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        # Get prediction and probabilities
        pred = self.model.predict(X_scaled)[0]
        proba = self.model.predict_proba(X_scaled)[0]
        confidence = float(max(proba))
        
        return self._reverse_mapping.get(pred, GamePhase.UNKNOWN), confidence
    
    def train(
        self, 
        features: np.ndarray, 
        labels: List[GamePhase]
    ) -> dict:
        """
        Train the classifier on labeled data.
        
        Args:
            features: 2D array (n_samples, n_features)
            labels: List of GamePhase labels
            
        Returns:
            Dict with training metrics
        """
        if len(features) == 0 or len(labels) == 0:
            raise ValueError("Cannot train on empty data")
        
        # Convert labels to integers
        y = np.array([self._label_mapping[label] for label in labels])
        
        # Scale features
        X_scaled = self.scaler.fit_transform(features)
        
        # Train model
        self.model.fit(X_scaled, y)
        self._is_trained = True
        
        # Calculate metrics using cross-validation
        cv_scores = cross_val_score(
            self.model, X_scaled, y, cv=min(5, len(features)), scoring="accuracy"
        )
        
        # Get feature importances
        importances = dict(zip(
            PhaseFeatures.feature_names(),
            self.model.feature_importances_
        ))
        
        return {
            "accuracy": float(np.mean(cv_scores)),
            "accuracy_std": float(np.std(cv_scores)),
            "n_samples": len(features),
            "n_features": features.shape[1],
            "feature_importances": importances,
        }
    
    def is_trained(self) -> bool:
        """Check if model is trained."""
        return self._is_trained
    
    def save_model(self, path: str) -> None:
        """Save model and scaler to disk."""
        if not self._is_trained:
            raise ValueError("Cannot save untrained model")
        
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        
        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "label_mapping": self._label_mapping,
            "reverse_mapping": self._reverse_mapping,
        }
        joblib.dump(model_data, path)
    
    def load_model(self, path: str) -> None:
        """Load model and scaler from disk."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model not found: {path}")
        
        model_data = joblib.load(path)
        self.model = model_data["model"]
        self.scaler = model_data["scaler"]
        self._label_mapping = model_data["label_mapping"]
        self._reverse_mapping = model_data["reverse_mapping"]
        self._is_trained = True
