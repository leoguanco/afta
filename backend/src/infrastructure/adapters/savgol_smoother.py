"""
Savitzky-Golay Smoother Adapter - Infrastructure Layer

Implements SmoothingPort using scipy's Savitzky-Golay filter.
"""
from typing import List

from src.domain.services.trajectory_smoother import SmoothingPort


class SavitzkyGolaySmoother(SmoothingPort):
    """
    Infrastructure adapter for Savitzky-Golay smoothing.
    
    Uses scipy.signal.savgol_filter for polynomial smoothing.
    Good for preserving peaks while reducing noise.
    """
    
    def __init__(self, poly_order: int = 2):
        """
        Initialize smoother.
        
        Args:
            poly_order: Order of polynomial to fit (default: 2 for quadratic)
        """
        self.poly_order = poly_order
    
    def smooth(self, values: List[float], window_size: int = 5) -> List[float]:
        """
        Apply Savitzky-Golay filter to values.
        
        Args:
            values: Sequence of values to smooth
            window_size: Filter window length (must be odd)
            
        Returns:
            Smoothed values as list
        """
        if len(values) < window_size:
            return values
        
        # Ensure window_size is odd
        if window_size % 2 == 0:
            window_size += 1
        
        # Polynomial order must be less than window size
        poly_order = min(self.poly_order, window_size - 1)
        
        try:
            from scipy.signal import savgol_filter
            import numpy as np
            
            smoothed = savgol_filter(
                np.array(values), 
                window_length=window_size, 
                polyorder=poly_order
            )
            return smoothed.tolist()
        except ImportError:
            # Fallback: simple moving average if scipy not available
            return self._simple_moving_average(values, window_size)
    
    def _simple_moving_average(self, values: List[float], window_size: int) -> List[float]:
        """Fallback smoothing using simple moving average."""
        if len(values) < window_size:
            return values
        
        result = []
        half_window = window_size // 2
        
        for i in range(len(values)):
            start = max(0, i - half_window)
            end = min(len(values), i + half_window + 1)
            window = values[start:end]
            result.append(sum(window) / len(window))
        
        return result
