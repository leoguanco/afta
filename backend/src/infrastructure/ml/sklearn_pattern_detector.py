"""
SklearnPatternDetector - Infrastructure Layer

ML adapter implementing PatternDetectorPort using scikit-learn clustering.
"""
from typing import List, Optional
import numpy as np
import uuid

from src.domain.ports.pattern_detector_port import PatternDetectorPort
from src.domain.entities.possession_sequence import PossessionSequence
from src.domain.entities.tactical_pattern import TacticalPattern


class SklearnPatternDetector(PatternDetectorPort):
    """
    Pattern detection using scikit-learn clustering algorithms.
    
    Supports K-means (default) and DBSCAN.
    """
    
    def __init__(self, algorithm: str = "kmeans"):
        """
        Initialize detector.
        
        Args:
            algorithm: "kmeans" or "dbscan"
        """
        self.algorithm = algorithm
        self.model = None
        self.scaler = None
        self.cluster_labels_ = None
        self.centroids_ = None
    
    def fit(self, sequences: List[PossessionSequence], n_clusters: int = 8) -> None:
        """Fit clustering model on sequences."""
        # Lazy imports
        from sklearn.cluster import KMeans, DBSCAN
        from sklearn.preprocessing import StandardScaler
        
        if not sequences:
            return
        
        # Extract feature vectors
        X = np.array([seq.extract_features().to_vector() for seq in sequences])
        
        # Standardize features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit clustering model
        if self.algorithm == "dbscan":
            self.model = DBSCAN(eps=0.5, min_samples=3)
        else:
            self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        
        self.cluster_labels_ = self.model.fit_predict(X_scaled)
        
        # Store centroids for K-means
        if hasattr(self.model, 'cluster_centers_'):
            self.centroids_ = self.model.cluster_centers_
    
    def predict_cluster(self, sequence: PossessionSequence) -> int:
        """Predict cluster for a single sequence."""
        if self.model is None or self.scaler is None:
            return -1
        
        features = sequence.extract_features().to_vector().reshape(1, -1)
        features_scaled = self.scaler.transform(features)
        
        if hasattr(self.model, 'predict'):
            return int(self.model.predict(features_scaled)[0])
        else:
            # DBSCAN doesn't have predict, find nearest cluster
            return -1
    
    def get_patterns(
        self,
        sequences: List[PossessionSequence],
        match_id: str,
        team_id: str
    ) -> List[TacticalPattern]:
        """Create TacticalPattern entities from clusters."""
        if self.cluster_labels_ is None:
            return []
        
        # Import labeler from domain layer
        from src.domain.services.pattern_labeler import PatternLabeler
        labeler = PatternLabeler()
        
        # Group sequences by cluster
        unique_labels = set(self.cluster_labels_)
        patterns = []
        
        for cluster_label in unique_labels:
            if cluster_label == -1:  # Skip noise in DBSCAN
                continue
            
            pattern_id = str(uuid.uuid4())[:8]
            
            # Get centroid if available
            centroid = None
            if self.centroids_ is not None and cluster_label < len(self.centroids_):
                centroid = self.centroids_[cluster_label].tolist()
            
            # Create pattern
            pattern = TacticalPattern(
                pattern_id=pattern_id,
                match_id=match_id,
                team_id=team_id,
                cluster_label=int(cluster_label),
                centroid=centroid
            )
            
            # Add sequences to pattern
            for i, seq in enumerate(sequences):
                if self.cluster_labels_[i] == cluster_label:
                    features = seq.extract_features()
                    pattern.add_sequence(
                        sequence_id=seq.sequence_id,
                        ended_in_shot=features.ended_in_shot,
                        ended_in_goal=features.ended_in_goal,
                        duration=features.duration_seconds,
                        event_count=features.event_count,
                        xt_progression=features.xt_progression
                    )
            
            # Label pattern based on characteristics
            pattern.label = labeler.label_pattern(pattern)
            pattern.description = labeler.describe_pattern(pattern)
            
            patterns.append(pattern)
        
        # Sort by occurrence count
        patterns.sort(key=lambda p: p.occurrence_count, reverse=True)
        
        return patterns
