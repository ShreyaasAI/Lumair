import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
import joblib
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AQIModelTrainer:
    def __init__(self, model_path="./ml/models", data_path=None):
        self.model_path = model_path
        self.data_path = data_path
        self.model = None
        self.scaler = None
        
        # Create models directory if it doesn't exist
        os.makedirs(model_path, exist_ok=True)
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for model training"""
        df = df.copy()
        
        # Handle missing values
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        # Time-based features
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
        df['month'] = pd.to_datetime(df['timestamp']).dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Lag features (previous values)
        for col in ['aqi', 'pm25', 'pm10', 'temperature', 'humidity']:
            if col in df.columns:
                df[f'{col}_lag_1'] = df[col].shift(1)
                df[f'{col}_lag_24'] = df[col].shift(24)
        
        # Rolling averages
        for col in ['aqi', 'pm25', 'temperature']:
            if col in df.columns:
                df[f'{col}_rolling_mean_24'] = df[col].rolling(window=24, min_periods=1).mean()
        
        # Drop rows with NaN from lag features
        df = df.dropna()
        
        return df
    
    def train(self, df: pd.DataFrame, target_col='aqi'):
        """Train XGBoost model for AQI prediction"""
        logger.info("Preparing data for training...")
        
        # Prepare features
        df_prepared = self.prepare_features(df)
        
        if len(df_prepared) < 100:
            raise ValueError("Insufficient data for training. Need at least 100 records.")
        
        # Define feature columns
        feature_cols = [
            'pm25', 'pm10', 'o3', 'no2', 'so2', 'co',
            'temperature', 'humidity', 'wind_speed', 'pressure',
            'hour', 'day_of_week', 'month', 'is_weekend'
        ]
        
        # Add lag features
        lag_cols = [col for col in df_prepared.columns if 'lag' in col or 'rolling' in col]
        feature_cols.extend(lag_cols)
        
        # Filter to existing columns
        feature_cols = [col for col in feature_cols if col in df_prepared.columns]
        
        X = df_prepared[feature_cols]
        y = df_prepared[target_col]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        # Scale features
        logger.info("Scaling features...")
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train XGBoost model
        logger.info("Training XGBoost model...")
        self.model = XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_test_scaled, y_test)],
            verbose=False
        )
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        logger.info(f"Training R² score: {train_score:.4f}")
        logger.info(f"Testing R² score: {test_score:.4f}")
        
        # Save model and scaler
        self.save_model()
        
        return {
            "train_score": train_score,
            "test_score": test_score,
            "feature_count": len(feature_cols),
            "training_samples": len(X_train)
        }
    
    def save_model(self):
        """Save trained model and scaler"""
        model_file = os.path.join(self.model_path, "aqi_model.pkl")
        scaler_file = os.path.join(self.model_path, "scaler.pkl")
        
        joblib.dump(self.model, model_file)
        joblib.dump(self.scaler, scaler_file)
        
        logger.info(f"Model saved to {model_file}")
        logger.info(f"Scaler saved to {scaler_file}")
    
    def load_model(self):
        """Load trained model and scaler"""
        model_file = os.path.join(self.model_path, "aqi_model.pkl")
        scaler_file = os.path.join(self.model_path, "scaler.pkl")
        
        if os.path.exists(model_file) and os.path.exists(scaler_file):
            self.model = joblib.load(model_file)
            self.scaler = joblib.load(scaler_file)
            logger.info("Model and scaler loaded successfully")
            return True
        else:
            logger.warning("Model files not found")
            return False

if __name__ == "__main__":
    # Example usage for training
    from database import SessionLocal
    from data_collector import DataCollector
    
    db = SessionLocal()
    collector = DataCollector(db)
    
    # Get training data
    df = collector.get_training_data(days=90)
    
    if len(df) > 0:
        trainer = AQIModelTrainer()
        results = trainer.train(df)
        print(f"Training complete: {results}")
    else:
        print("No data available for training")
    
    db.close()