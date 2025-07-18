#!/usr/bin/env python3
"""
Discharge Prediction Model
Machine learning model to predict which patients will discharge tomorrow
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

class DischargePredictionModel:
    """ML model to predict next-day discharges for proactive planning"""
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        self.feature_names = None
        self.is_trained = False
        
    def create_features(self, df):
        """Engineer features for discharge prediction"""
        features = pd.DataFrame()
        
        # Length of stay features
        features['los_days'] = df['los_days']
        features['los_vs_expected'] = df['los_days'] / df['expected_los_days']
        features['los_category'] = pd.cut(df['los_days'], 
                                         bins=[0, 2, 4, 7, 14, 100], 
                                         labels=[1, 2, 3, 4, 5]).astype(int)
        
        # Time-based features
        features['admission_dow'] = df['admission_time'].dt.dayofweek
        features['current_dow'] = datetime.now().weekday()
        features['is_weekend'] = features['current_dow'].isin([5, 6]).astype(int)
        
        # Clinical features
        features['complexity_score'] = df['complexity_score']
        features['has_iv_meds'] = df['has_iv_medications'].astype(int)
        features['pending_labs'] = df['pending_lab_results']
        features['pending_consults'] = df['active_consults']
        features['vital_stability'] = df['vital_signs_stable'].astype(int)
        
        # Unit features (one-hot encoding)
        unit_dummies = pd.get_dummies(df['unit'], prefix='unit')
        features = pd.concat([features, unit_dummies], axis=1)
        
        # Disposition features
        disp_dummies = pd.get_dummies(df['discharge_disposition'], prefix='disposition')
        features = pd.concat([features, disp_dummies], axis=1)
        
        # Process indicators
        features['discharge_order_placed'] = df['discharge_order_placed'].astype(int)
        features['med_rec_complete'] = df['medication_reconciliation_complete'].astype(int)
        features['transport_arranged'] = df['transport_arranged'].astype(int)
        features['education_complete'] = df['education_complete'].astype(int)
        
        self.feature_names = features.columns.tolist()
        return features
    
    def generate_training_data(self, n_samples=5000):
        """Generate synthetic training data for demonstration"""
        np.random.seed(42)
        
        # Base patient data
        data = {
            'patient_id': range(n_samples),
            'admission_time': pd.date_range(end=datetime.now(), periods=n_samples, freq='6H'),
            'unit': np.random.choice(['Medical', 'Surgical', 'Cardiology', 'Orthopedics'], 
                                   n_samples, p=[0.4, 0.3, 0.2, 0.1]),
            'complexity_score': np.random.randint(1, 10, n_samples),
            'expected_los_days': np.random.choice([1, 2, 3, 4, 5, 7, 10], n_samples, 
                                                p=[0.1, 0.2, 0.3, 0.2, 0.1, 0.05, 0.05])
        }
        
        df = pd.DataFrame(data)
        
        # Calculate actual LOS based on expected with some variation
        df['los_days'] = df['expected_los_days'] * np.random.normal(1, 0.2, n_samples)
        df['los_days'] = df['los_days'].clip(lower=0.5)
        
        # Clinical indicators (correlated with discharge likelihood)
        discharge_prob = 1 / (1 + np.exp(-2 * (df['los_days'] / df['expected_los_days'] - 1)))
        
        df['has_iv_medications'] = np.random.binomial(1, 1 - discharge_prob * 0.7)
        df['pending_lab_results'] = np.random.poisson(2 * (1 - discharge_prob))
        df['active_consults'] = np.random.binomial(2, 1 - discharge_prob * 0.8)
        df['vital_signs_stable'] = np.random.binomial(1, 0.7 + discharge_prob * 0.25)
        
        # Discharge disposition
        df['discharge_disposition'] = np.random.choice(
            ['Home', 'SNF', 'Rehab', 'Home Health'], 
            n_samples, p=[0.6, 0.2, 0.1, 0.1]
        )
        
        # Process indicators
        df['discharge_order_placed'] = np.random.binomial(1, discharge_prob * 0.5)
        df['medication_reconciliation_complete'] = np.random.binomial(1, discharge_prob * 0.6)
        df['transport_arranged'] = np.random.binomial(1, discharge_prob * 0.4)
        df['education_complete'] = np.random.binomial(1, discharge_prob * 0.5)
        
        # Target: Will discharge tomorrow (binary)
        df['will_discharge_tomorrow'] = (
            (discharge_prob > 0.6) & 
            (df['vital_signs_stable'] == 1) & 
            (df['has_iv_medications'] == 0) & 
            (np.random.random(n_samples) > 0.3)
        ).astype(int)
        
        return df
    
    def train(self, X_train=None, y_train=None):
        """Train the discharge prediction model"""
        if X_train is None:
            # Generate training data if not provided
            print("Generating synthetic training data...")
            train_data = self.generate_training_data()
            X = self.create_features(train_data)
            y = train_data['will_discharge_tomorrow']
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
        else:
            X_test, y_test = None, None
        
        print("Training discharge prediction model...")
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        if X_test is not None:
            # Evaluate model
            y_pred = self.model.predict(X_test)
            print("\nModel Performance:")
            print(classification_report(y_test, y_pred))
            
            # Feature importance
            self.plot_feature_importance()
            
            # Confusion matrix
            self.plot_confusion_matrix(y_test, y_pred)
        
        return self
    
    def predict_discharge_probability(self, patient_features):
        """Predict probability of discharge tomorrow for given patients"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Ensure features match training features
        X = self.create_features(patient_features)
        
        # Get probability of discharge
        probabilities = self.model.predict_proba(X)[:, 1]
        
        # Create results DataFrame
        results = patient_features[['patient_id', 'unit', 'los_days']].copy()
        results['discharge_probability'] = probabilities
        results['prediction'] = (probabilities > 0.5).astype(int)
        results['confidence'] = np.abs(probabilities - 0.5) * 2
        
        return results.sort_values('discharge_probability', ascending=False)
    
    def plot_feature_importance(self, top_n=15):
        """Plot feature importance from the trained model"""
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False).head(top_n)
        
        plt.figure(figsize=(10, 6))
        plt.barh(importance_df['feature'], importance_df['importance'])
        plt.xlabel('Feature Importance')
        plt.title('Top Predictors of Next-Day Discharge')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.show()
        
        return importance_df
    
    def plot_confusion_matrix(self, y_true, y_pred):
        """Plot confusion matrix for model evaluation"""
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.title('Discharge Prediction Confusion Matrix')
        plt.show()
    
    def generate_daily_predictions(self, current_patients):
        """Generate predictions for all current inpatients"""
        predictions = self.predict_discharge_probability(current_patients)
        
        # Group by unit
        unit_summary = predictions.groupby('unit').agg({
            'patient_id': 'count',
            'prediction': 'sum',
            'discharge_probability': 'mean'
        }).round(2)
        unit_summary.columns = ['Total Patients', 'Predicted Discharges', 'Avg Probability']
        
        print("\n=== DISCHARGE PREDICTIONS FOR TOMORROW ===")
        print(f"\nTotal Patients: {len(predictions)}")
        print(f"Predicted Discharges: {predictions['prediction'].sum()}")
        print(f"High Confidence (>80%): {len(predictions[predictions['discharge_probability'] > 0.8])}")
        
        print("\nBy Unit:")
        print(unit_summary)
        
        print("\nTop 10 Most Likely Discharges:")
        top_10 = predictions.head(10)[['patient_id', 'unit', 'los_days', 'discharge_probability']]
        print(top_10.to_string(index=False))
        
        return predictions
    
    def save_model(self, filepath='discharge_prediction_model.pkl'):
        """Save trained model to disk"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='discharge_prediction_model.pkl'):
        """Load trained model from disk"""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        self.is_trained = True
        print(f"Model loaded from {filepath}")


def generate_mock_current_patients(n=50):
    """Generate mock data for current inpatients"""
    np.random.seed(123)
    
    patients = {
        'patient_id': [f'P{i:04d}' for i in range(n)],
        'admission_time': pd.date_range(end=datetime.now(), periods=n, freq='12H'),
        'unit': np.random.choice(['Medical', 'Surgical', 'Cardiology', 'Orthopedics'], n),
        'complexity_score': np.random.randint(1, 10, n),
        'expected_los_days': np.random.choice([1, 2, 3, 4, 5, 7], n),
        'los_days': np.random.uniform(0.5, 10, n),
        'has_iv_medications': np.random.binomial(1, 0.3, n),
        'pending_lab_results': np.random.poisson(1, n),
        'active_consults': np.random.binomial(2, 0.2, n),
        'vital_signs_stable': np.random.binomial(1, 0.85, n),
        'discharge_disposition': np.random.choice(['Home', 'SNF', 'Rehab', 'Home Health'], n),
        'discharge_order_placed': np.random.binomial(1, 0.1, n),
        'medication_reconciliation_complete': np.random.binomial(1, 0.3, n),
        'transport_arranged': np.random.binomial(1, 0.2, n),
        'education_complete': np.random.binomial(1, 0.25, n)
    }
    
    return pd.DataFrame(patients)


def main():
    """Example usage of the discharge prediction model"""
    print("=== Discharge Prediction Model Demo ===\n")
    
    # Initialize and train model
    model = DischargePredictionModel()
    model.train()
    
    # Generate predictions for current patients
    print("\nGenerating predictions for current inpatients...")
    current_patients = generate_mock_current_patients()
    predictions = model.generate_daily_predictions(current_patients)
    
    # Save model
    model.save_model()
    
    print("\n✓ Discharge prediction model ready for use!")


if __name__ == "__main__":
    main()