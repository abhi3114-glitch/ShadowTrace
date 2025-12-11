import pandas as pd
from sklearn.cluster import KMeans
import numpy as np

class MovementAnalyzer:
    def __init__(self):
        pass

    def run_clustering(self, data: pd.DataFrame, n_clusters=3):
        """
        Simple K-Means clustering on Accelerometer data to find 'Locations' (e.g. tilted on lap vs flat on desk).
        """
        if data.empty or len(data) < n_clusters:
            return data

        features = data[['acc_x', 'acc_y', 'acc_z']]
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        data['cluster_id'] = kmeans.fit_predict(features)
        
        return data

    def calculate_daily_stat(self, data: pd.DataFrame):
        """
        Calculate daily total movement time.
        Usually called on 'sensor_logs'.
        """
        if data.empty:
            return 0
        
        # Assuming 5Hz sample rate or calculate from timestamps if irregular
        # Simple count of moving frames if we have strict sampling
        moving_frames = data[data['is_moving'] == True] # bool check
        
        # Estimation: count * (1/sampling_rate approx) -> easier if we just rely on rows
        return len(moving_frames)
