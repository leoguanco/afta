"""
TDD Tests for SklearnPhaseClassifier.
"""
import pytest
import numpy as np
import tempfile
import os

from src.infrastructure.ml.sklearn_phase_classifier import SklearnPhaseClassifier
from src.domain.value_objects.game_phase import GamePhase
from src.domain.value_objects.phase_features import PhaseFeatures


class TestSklearnPhaseClassifier:
    """Test suite for SklearnPhaseClassifier."""

    @pytest.fixture
    def classifier(self):
        """Create a fresh classifier."""
        return SklearnPhaseClassifier(n_estimators=10, random_state=42)

    @pytest.fixture
    def sample_features(self):
        """Create sample PhaseFeatures."""
        return PhaseFeatures(
            home_centroid_x=30.0,
            home_centroid_y=34.0,
            away_centroid_x=75.0,
            away_centroid_y=34.0,
            home_spread_x=15.0,
            home_spread_y=10.0,
            away_spread_x=12.0,
            away_spread_y=8.0,
            ball_x=35.0,
            ball_y=34.0,
            ball_velocity_x=2.0,
            ball_velocity_y=0.5,
            home_defensive_line=15.0,
            away_defensive_line=85.0,
            home_possession_prob=0.8,
        )

    @pytest.fixture
    def training_data(self):
        """Create synthetic training data."""
        np.random.seed(42)
        n_samples = 100
        
        # Generate features for each phase
        features = []
        labels = []
        
        for _ in range(n_samples // 4):
            # Organized Attack: ball in opponent half, team pushed up
            f = np.array([70, 34, 40, 34, 15, 10, 12, 8, 75, 34, 3, 0, 55, 25, 0.9])
            f += np.random.randn(15) * 2
            features.append(f)
            labels.append(GamePhase.ORGANIZED_ATTACK)
            
            # Organized Defense: ball in own half, team defending
            f = np.array([30, 34, 60, 34, 10, 8, 15, 10, 25, 34, -2, 0, 20, 70, 0.2])
            f += np.random.randn(15) * 2
            features.append(f)
            labels.append(GamePhase.ORGANIZED_DEFENSE)
            
            # Transition ATK->DEF: just lost ball
            f = np.array([60, 34, 50, 34, 20, 15, 15, 12, 55, 40, -5, 2, 40, 50, 0.3])
            f += np.random.randn(15) * 2
            features.append(f)
            labels.append(GamePhase.TRANSITION_ATK_DEF)
            
            # Transition DEF->ATK: just won ball
            f = np.array([40, 34, 55, 34, 15, 10, 18, 14, 45, 30, 4, -1, 30, 60, 0.7])
            f += np.random.randn(15) * 2
            features.append(f)
            labels.append(GamePhase.TRANSITION_DEF_ATK)
        
        return np.array(features), labels

    def test_is_not_trained_initially(self, classifier):
        """Classifier should not be trained initially."""
        assert classifier.is_trained() is False

    def test_classify_returns_unknown_when_not_trained(self, classifier, sample_features):
        """Should return UNKNOWN when not trained."""
        result = classifier.classify(sample_features)
        assert result == GamePhase.UNKNOWN

    def test_train_model(self, classifier, training_data):
        """Should train model and return metrics."""
        features, labels = training_data
        
        metrics = classifier.train(features, labels)
        
        assert classifier.is_trained() is True
        assert "accuracy" in metrics
        assert metrics["accuracy"] > 0.5  # Should be better than random
        assert metrics["n_samples"] == len(labels)
        assert "feature_importances" in metrics

    def test_classify_after_training(self, classifier, training_data, sample_features):
        """Should classify correctly after training."""
        features, labels = training_data
        classifier.train(features, labels)
        
        result = classifier.classify(sample_features)
        
        # Should return a valid phase (not UNKNOWN)
        assert result in GamePhase
        assert result != GamePhase.UNKNOWN

    def test_classify_batch(self, classifier, training_data):
        """Should classify batch of features."""
        features, labels = training_data
        classifier.train(features, labels)
        
        # Create batch of features
        batch = [
            PhaseFeatures(*features[0]),
            PhaseFeatures(*features[1]),
            PhaseFeatures(*features[2]),
        ]
        
        results = classifier.classify_batch(batch)
        
        assert len(results) == 3
        assert all(r in GamePhase for r in results)

    def test_classify_with_confidence(self, classifier, training_data, sample_features):
        """Should return confidence score with classification."""
        features, labels = training_data
        classifier.train(features, labels)
        
        phase, confidence = classifier.classify_with_confidence(sample_features)
        
        assert phase in GamePhase
        assert 0.0 <= confidence <= 1.0

    def test_save_and_load_model(self, classifier, training_data):
        """Should save and load model correctly."""
        features, labels = training_data
        classifier.train(features, labels)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = os.path.join(tmpdir, "model.joblib")
            classifier.save_model(model_path)
            
            # Create new classifier and load
            new_classifier = SklearnPhaseClassifier()
            new_classifier.load_model(model_path)
            
            assert new_classifier.is_trained() is True
            
            # Should produce same results
            sample = PhaseFeatures(*features[0])
            orig_result = classifier.classify(sample)
            loaded_result = new_classifier.classify(sample)
            assert orig_result == loaded_result

    def test_train_empty_data_raises(self, classifier):
        """Should raise error on empty training data."""
        with pytest.raises(ValueError):
            classifier.train(np.array([]), [])

    def test_save_untrained_raises(self, classifier):
        """Should raise error when saving untrained model."""
        with pytest.raises(ValueError):
            classifier.save_model("model.joblib")
