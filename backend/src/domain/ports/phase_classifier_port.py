"""
PhaseClassifierPort - Domain Layer

Interface for ML-based phase classification.
"""
from abc import ABC, abstractmethod
from typing import List
import numpy as np

from src.domain.value_objects.game_phase import GamePhase
from src.domain.value_objects.phase_features import PhaseFeatures


class PhaseClassifierPort(ABC):
    """
    Port for phase classification models.
    
    This interface allows different ML implementations
    (scikit-learn, PyTorch, etc.) to be used for classification.
    """
    
    @abstractmethod
    def classify(self, features: PhaseFeatures) -> GamePhase:
        """
        Classify a single frame's features into a game phase.
        
        Args:
            features: PhaseFeatures for a single frame
            
        Returns:
            Predicted GamePhase
        """
        pass
    
    @abstractmethod
    def classify_batch(self, features_list: List[PhaseFeatures]) -> List[GamePhase]:
        """
        Classify multiple frames in batch for efficiency.
        
        Args:
            features_list: List of PhaseFeatures
            
        Returns:
            List of predicted GamePhases
        """
        pass
    
    @abstractmethod
    def classify_with_confidence(
        self, features: PhaseFeatures
    ) -> tuple[GamePhase, float]:
        """
        Classify with confidence score.
        
        Args:
            features: PhaseFeatures for a single frame
            
        Returns:
            Tuple of (predicted GamePhase, confidence 0-1)
        """
        pass
    
    @abstractmethod
    def train(
        self, 
        features: np.ndarray, 
        labels: List[GamePhase]
    ) -> dict:
        """
        Train the classifier on labeled data.
        
        Args:
            features: 2D numpy array of shape (n_samples, n_features)
            labels: List of GamePhase labels
            
        Returns:
            Training metrics dict (accuracy, f1, etc.)
        """
        pass
    
    @abstractmethod
    def is_trained(self) -> bool:
        """Check if the model has been trained."""
        pass
