import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import os
from typing import Dict, List
from services.weather_service import WeatherService
from services.aqi_service import AQIService
import logging

logger = logging.getLogger(__name__)

class AQIPredictor:
    def __init__(self, model_path="./ml/models"):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.weather_service = WeatherService()
        self.aqi_service = AQIService()
        self.load_model()
    
    def load_model(self):
        """Load trained model and scaler"""
        model_file = os.path.join(self.model_path, "aqi_model.pkl")
        scaler_file = os.path.join(self.model_path, "scaler.pkl")
        
        try:
            self.model = joblib.load(model_file)
            self.scaler = joblib.load(scaler_file)
            logger.info("Predictor loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def prepare_prediction_features(
        self, 
        current_data: Dict, 
        forecast_data: Dict,
        historical_data: pd.DataFrame = None
    ) -> pd.DataFrame:
        """Prepare features for prediction"""
        
        # Base features from current data and forecast
        features = {
            'pm25': current_data.get('pm25', 0),
            'pm10': current_data.get('pm10', 0),
            'o3': current_data.get('o3', 0),
            'no2': current_data.get('no2', 0),
            'so2': current_data.get('so2', 0),
            'co': current_data.get('co', 0),
            'temperature': forecast_data.get('temperature', current_data.get('temperature', 20)),
            'humidity': forecast_data.get('humidity', current_data.get('humidity', 50)),
            'wind_speed': forecast_data.get('wind_speed', current_data.get('wind_speed', 5)),
            'pressure': forecast_data.get('pressure', current_data.get('pressure', 1013)),
        }
        
        # Time features
        forecast_time = datetime.utcnow() + timedelta(hours=forecast_data.get('hours_ahead', 24))
        features['hour'] = forecast_time.hour
        features['day_of_week'] = forecast_time.weekday()
        features['month'] = forecast_time.month
        features['is_weekend'] = 1 if forecast_time.weekday() in [5, 6] else 0
        
        # Lag features (using current as lag)
        current_aqi = current_data.get('aqi', 50)
        features['aqi_lag_1'] = current_aqi
        features['aqi_lag_24'] = current_aqi
        features['pm25_lag_1'] = features['pm25']
        features['pm25_lag_24'] = features['pm25']
        features['pm10_lag_1'] = features['pm10']
        features['pm10_lag_24'] = features['pm10']
        features['temperature_lag_1'] = current_data.get('temperature', features['temperature'])
        features['temperature_lag_24'] = current_data.get('temperature', features['temperature'])
        features['humidity_lag_1'] = current_data.get('humidity', features['humidity'])
        features['humidity_lag_24'] = current_data.get('humidity', features['humidity'])
        
        # Rolling averages (using current values)
        features['aqi_rolling_mean_24'] = current_aqi
        features['pm25_rolling_mean_24'] = features['pm25']
        features['temperature_rolling_mean_24'] = features['temperature']
        
        return pd.DataFrame([features])
    
    def predict_future_aqi(
        self, 
        lat: float, 
        lon: float, 
        city: str,
        hours: List[int] = [24, 48, 72]
    ) -> Dict:
        """Predict AQI for future time periods"""
        
        if not self.model or not self.scaler:
            logger.error("Model not loaded")
            return None
        
        try:
            # Get current AQI data
            current_aqi = self.aqi_service.get_current_aqi(lat, lon)
            if not current_aqi:
                logger.warning(f"No current AQI data for {city}")
                current_aqi = {'aqi': 50}  # Default fallback
            
            # Get weather forecast
            weather_forecast = self.weather_service.get_forecast(lat, lon, hours=max(hours))
            if not weather_forecast:
                logger.warning(f"No weather forecast for {city}")
                return None
            
            predictions = []
            
            for hour in hours:
                # Find closest forecast data point
                forecast_idx = min(hour // 3, len(weather_forecast) - 1)
                forecast_data = weather_forecast[forecast_idx].copy()
                forecast_data['hours_ahead'] = hour
                
                # Prepare features
                features_df = self.prepare_prediction_features(
                    current_aqi,
                    forecast_data
                )
                
                # Scale features
                features_scaled = self.scaler.transform(features_df)
                
                # Predict
                predicted_aqi = self.model.predict(features_scaled)[0]
                predicted_aqi = max(0, min(500, predicted_aqi))  # Clamp to valid range
                
                predictions.append({
                    'hours': hour,
                    'timestamp': (datetime.utcnow() + timedelta(hours=hour)).isoformat(),
                    'predicted_aqi': round(float(predicted_aqi), 1),
                    'temperature': forecast_data.get('temperature'),
                    'humidity': forecast_data.get('humidity')
                })
            
            return {
                'city': city,
                'current_aqi': float(current_aqi.get('aqi', 0)),
                'predictions': predictions,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting AQI: {e}")
            return None
    
    def predict_with_fallback(
        self,
        lat: float,
        lon: float,
        city: str,
        hours: List[int] = [24, 48, 72]
    ) -> Dict:
        """Predict with fallback to simple trend-based prediction"""
        
        result = self.predict_future_aqi(lat, lon, city, hours)
        
        if result:
            return result
        
        # Fallback: simple trend-based prediction
        logger.info("Using fallback prediction method")
        current_aqi_data = self.aqi_service.get_current_aqi(lat, lon)
        current_aqi = current_aqi_data.get('aqi', 50) if current_aqi_data else 50
        
        predictions = []
        for hour in hours:
            # Simple decay model with weather influence
            decay_factor = 0.95 ** (hour / 24)
            predicted = current_aqi * decay_factor
            
            predictions.append({
                'hours': hour,
                'timestamp': (datetime.utcnow() + timedelta(hours=hour)).isoformat(),
                'predicted_aqi': round(float(predicted), 1),
                'temperature': None,
                'humidity': None
            })
        
        return {
            'city': city,
            'current_aqi': float(current_aqi),
            'predictions': predictions,
            'generated_at': datetime.utcnow().isoformat(),
            'fallback': True
        }