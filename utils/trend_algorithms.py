"""
Trend Detection Algorithms
Advanced algorithms for trend analysis and anomaly detection
"""

from typing import List, Tuple, Dict, Any
from datetime import datetime
import math


# ============================================================================
# LINEAR REGRESSION
# ============================================================================

def linear_regression(data_points: List[Tuple[float, float]]) -> Tuple[float, float]:
    """
    Simple linear regression: y = mx + b
    
    Args:
        data_points: List of (x, y) tuples
        
    Returns:
        (slope, intercept)
    """
    if len(data_points) < 2:
        return (0.0, 0.0)
    
    n = len(data_points)
    x_values = [p[0] for p in data_points]
    y_values = [p[1] for p in data_points]
    
    x_mean = sum(x_values) / n
    y_mean = sum(y_values) / n
    
    # Calculate slope
    numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
    denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return (0.0, y_mean)
    
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    
    return (slope, intercept)


def calculate_r_squared(
    data_points: List[Tuple[float, float]],
    slope: float,
    intercept: float
) -> float:
    """
    Calculate R² (coefficient of determination) to measure fit quality
    
    Returns: 0-1, where 1 is perfect fit
    """
    if len(data_points) < 2:
        return 0.0
    
    y_values = [p[1] for p in data_points]
    y_mean = sum(y_values) / len(y_values)
    
    # Total sum of squares
    ss_tot = sum((y - y_mean) ** 2 for y in y_values)
    
    # Residual sum of squares
    ss_res = sum((y_values[i] - (slope * data_points[i][0] + intercept)) ** 2 
                 for i in range(len(data_points)))
    
    if ss_tot == 0:
        return 0.0
    
    r_squared = 1 - (ss_res / ss_tot)
    return max(0, min(1, r_squared))


# ============================================================================
# MOVING AVERAGE
# ============================================================================

def simple_moving_average(values: List[float], window_size: int = 3) -> List[float]:
    """
    Calculate simple moving average
    
    Args:
        values: List of values
        window_size: Size of moving window
        
    Returns:
        List of moving averages (same length as input)
    """
    if len(values) < window_size:
        return values
    
    result = []
    for i in range(len(values)):
        if i < window_size - 1:
            # Not enough data for full window, use available data
            window = values[:i+1]
        else:
            window = values[i-window_size+1:i+1]
        
        result.append(sum(window) / len(window))
    
    return result


def exponential_moving_average(
    values: List[float],
    alpha: float = 0.3
) -> List[float]:
    """
    Calculate exponential moving average (EMA)
    
    Args:
        values: List of values
        alpha: Smoothing factor (0-1), higher = more weight on recent values
        
    Returns:
        List of EMAs
    """
    if not values:
        return []
    
    ema = [values[0]]
    
    for i in range(1, len(values)):
        new_ema = alpha * values[i] + (1 - alpha) * ema[-1]
        ema.append(new_ema)
    
    return ema


# ============================================================================
# MOMENTUM CALCULATION
# ============================================================================

def calculate_momentum(values: List[float], period: int = 5) -> List[float]:
    """
    Calculate momentum (rate of change)
    
    Momentum[i] = (Value[i] - Value[i-period]) / period
    
    Returns:
        List of momentum values
    """
    if len(values) < period + 1:
        return [0.0] * len(values)
    
    momentum = [0.0] * period
    
    for i in range(period, len(values)):
        change = values[i] - values[i - period]
        momentum.append(change / period)
    
    return momentum


def calculate_acceleration(momentum: List[float]) -> List[float]:
    """
    Calculate acceleration (change in momentum)
    
    Acceleration[i] = Momentum[i] - Momentum[i-1]
    """
    if len(momentum) < 2:
        return [0.0] * len(momentum)
    
    acceleration = [0.0]
    
    for i in range(1, len(momentum)):
        acceleration.append(momentum[i] - momentum[i-1])
    
    return acceleration


# ============================================================================
# ANOMALY DETECTION
# ============================================================================

def detect_anomalies_zscore(
    values: List[float],
    threshold: float = 2.0
) -> List[Dict[str, Any]]:
    """
    Detect anomalies using Z-score method

    Args:
        values: List of values
        threshold: Z-score threshold (default 2.0 = ~95% confidence)

    Returns:
        List of anomalies with index and z-score
    """
    if len(values) < 3:
        return []

    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std_dev = math.sqrt(variance)

    if std_dev == 0:
        return []

    anomalies = []
    for i, value in enumerate(values):
        z_score = (value - mean) / std_dev

        if abs(z_score) > threshold:
            anomalies.append({
                "index": i,
                "value": value,
                "z_score": round(z_score, 2),
                "type": "spike" if z_score > 0 else "drop"
            })

    return anomalies


def detect_anomalies_iqr(values: List[float]) -> List[Dict[str, Any]]:
    """
    Detect anomalies using Interquartile Range (IQR) method

    More robust to outliers than Z-score
    """
    if len(values) < 4:
        return []

    sorted_values = sorted(values)
    n = len(sorted_values)

    # Calculate Q1 and Q3
    q1_index = n // 4
    q3_index = 3 * n // 4

    q1 = sorted_values[q1_index]
    q3 = sorted_values[q3_index]
    iqr = q3 - q1

    # Calculate bounds
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    anomalies = []
    for i, value in enumerate(values):
        if value < lower_bound or value > upper_bound:
            anomalies.append({
                "index": i,
                "value": value,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "type": "spike" if value > upper_bound else "drop"
            })

    return anomalies


def detect_sudden_changes(
    values: List[float],
    threshold_percent: float = 20.0
) -> List[Dict[str, Any]]:
    """
    Detect sudden changes (jumps or drops) between consecutive values

    Args:
        values: List of values
        threshold_percent: % change threshold to flag as sudden

    Returns:
        List of sudden changes
    """
    if len(values) < 2:
        return []

    changes = []

    for i in range(1, len(values)):
        if values[i-1] == 0:
            continue

        percent_change = abs((values[i] - values[i-1]) / values[i-1] * 100)

        if percent_change > threshold_percent:
            changes.append({
                "index": i,
                "from_value": values[i-1],
                "to_value": values[i],
                "percent_change": round(percent_change, 2),
                "type": "jump" if values[i] > values[i-1] else "drop"
            })

    return changes


# ============================================================================
# TREND STRENGTH INDICATORS
# ============================================================================

def calculate_trend_strength(
    values: List[float],
    window_size: int = 5
) -> float:
    """
    Calculate trend strength (0-1)

    Uses correlation between values and their indices
    Higher value = stronger trend
    """
    if len(values) < window_size:
        return 0.0

    # Use last window_size values
    recent_values = values[-window_size:]
    indices = list(range(len(recent_values)))

    # Calculate correlation
    n = len(recent_values)
    mean_x = sum(indices) / n
    mean_y = sum(recent_values) / n

    numerator = sum((indices[i] - mean_x) * (recent_values[i] - mean_y) for i in range(n))

    sum_sq_x = sum((x - mean_x) ** 2 for x in indices)
    sum_sq_y = sum((y - mean_y) ** 2 for y in recent_values)

    denominator = math.sqrt(sum_sq_x * sum_sq_y)

    if denominator == 0:
        return 0.0

    correlation = numerator / denominator

    # Return absolute correlation (strength regardless of direction)
    return abs(correlation)


def calculate_volatility(values: List[float]) -> float:
    """
    Calculate volatility (standard deviation of returns)

    Higher value = more volatile
    """
    if len(values) < 2:
        return 0.0

    # Calculate returns (percent changes)
    returns = []
    for i in range(1, len(values)):
        if values[i-1] != 0:
            ret = (values[i] - values[i-1]) / values[i-1]
            returns.append(ret)

    if not returns:
        return 0.0

    # Calculate standard deviation of returns
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    volatility = math.sqrt(variance)

    return volatility


def predict_next_value(
    values: List[float],
    method: str = "linear"
) -> float:
    """
    Predict next value using specified method

    Args:
        values: Historical values
        method: "linear"|"ema"|"momentum"

    Returns:
        Predicted next value
    """
    if not values:
        return 0.0

    if len(values) == 1:
        return values[0]

    if method == "linear":
        # Use linear regression
        data_points = [(i, values[i]) for i in range(len(values))]
        slope, intercept = linear_regression(data_points)
        next_x = len(values)
        return slope * next_x + intercept

    elif method == "ema":
        # Use exponential moving average
        ema_values = exponential_moving_average(values)
        return ema_values[-1]

    elif method == "momentum":
        # Use momentum-based prediction
        if len(values) < 3:
            return values[-1]

        momentum_values = calculate_momentum(values, period=min(3, len(values) - 1))
        recent_momentum = momentum_values[-1]
        return values[-1] + recent_momentum

    else:
        # Default: return last value
        return values[-1]


