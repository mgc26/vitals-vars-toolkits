#!/usr/bin/env python3
"""
Machine Learning Framework for Avatar Patient Selection
Identifies patients most likely to benefit from avatar interventions
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import roc_auc_score, precision_recall_curve, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

class MLPatientSelector:
    """ML-based patient selection for avatar interventions"""
    
    def __init__(self):
        """Initialize patient selection framework"""
        self.scaler = StandardScaler()
        self.models = {}
        self.phenotypes = None
        
    def create_patient_features(self, n_patients: int = 1000) -> pd.DataFrame:
        """
        Generate synthetic patient data for demonstration
        
        Args:
            n_patients: Number of synthetic patients
            
        Returns:
            DataFrame with patient features
        """
        np.random.seed(42)
        
        # Demographics
        age = np.random.normal(65, 15, n_patients)
        age = np.clip(age, 18, 95).astype(int)
        
        # Clinical factors
        comorbidity_count = np.random.poisson(2, n_patients)
        prior_admissions = np.random.poisson(1.5, n_patients)
        
        # Technology factors
        tech_comfort = np.random.beta(2, 5, n_patients) * 10  # Skewed low
        has_smartphone = np.random.binomial(1, 0.6, n_patients)
        
        # Social factors
        lives_alone = np.random.binomial(1, 0.3, n_patients)
        english_primary = np.random.binomial(1, 0.85, n_patients)
        health_literacy = np.random.beta(3, 2, n_patients) * 5
        
        # Risk scores
        readmission_risk = (
            0.1 + 
            0.05 * (age > 75) +
            0.03 * comorbidity_count +
            0.04 * prior_admissions +
            0.02 * lives_alone +
            np.random.normal(0, 0.05, n_patients)
        )
        readmission_risk = np.clip(readmission_risk, 0, 1)
        
        # Medication factors
        medication_count = np.random.poisson(5, n_patients)
        adherence_score = np.random.beta(4, 2, n_patients)
        
        # Create outcome: would benefit from avatar (synthetic)
        benefit_probability = (
            0.3 +
            0.1 * (tech_comfort > 5) +
            0.15 * (health_literacy < 3) +
            0.1 * (readmission_risk > 0.2) +
            0.1 * (medication_count > 7) +
            0.05 * english_primary +
            -0.1 * (age > 80) +
            np.random.normal(0, 0.1, n_patients)
        )
        benefit_probability = np.clip(benefit_probability, 0, 1)
        would_benefit = np.random.binomial(1, benefit_probability, n_patients)
        
        # Engagement likelihood
        engagement_score = (
            0.5 +
            0.2 * (tech_comfort / 10) +
            0.1 * has_smartphone +
            -0.1 * (age > 75) +
            0.1 * (health_literacy / 5) +
            np.random.normal(0, 0.1, n_patients)
        )
        engagement_score = np.clip(engagement_score, 0, 1)
        
        return pd.DataFrame({
            'patient_id': [f'P{i:04d}' for i in range(n_patients)],
            'age': age,
            'comorbidity_count': comorbidity_count,
            'prior_admissions_12mo': prior_admissions,
            'tech_comfort_score': tech_comfort,
            'has_smartphone': has_smartphone,
            'lives_alone': lives_alone,
            'english_primary_language': english_primary,
            'health_literacy_score': health_literacy,
            'readmission_risk_score': readmission_risk,
            'medication_count': medication_count,
            'adherence_score': adherence_score,
            'would_benefit': would_benefit,
            'engagement_likelihood': engagement_score
        })
    
    def identify_patient_phenotypes(self, 
                                   data: pd.DataFrame,
                                   n_clusters: int = 4) -> pd.DataFrame:
        """
        Use clustering to identify patient phenotypes
        
        Args:
            data: Patient feature DataFrame
            n_clusters: Number of phenotypes to identify
            
        Returns:
            Data with phenotype assignments
        """
        # Select features for clustering
        cluster_features = [
            'age', 'comorbidity_count', 'tech_comfort_score',
            'health_literacy_score', 'readmission_risk_score',
            'medication_count', 'adherence_score'
        ]
        
        X = data[cluster_features].values
        X_scaled = self.scaler.fit_transform(X)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        data['phenotype'] = clusters
        
        # Characterize phenotypes
        phenotype_names = {
            0: 'Tech-Savvy Low-Risk',
            1: 'High-Risk Complex',
            2: 'Elderly Low-Literacy',
            3: 'Moderate-Risk Engaged'
        }
        
        # Analyze phenotypes
        for i in range(n_clusters):
            mask = data['phenotype'] == i
            subset = data[mask]
            
            # Determine characteristics
            if subset['age'].mean() > 70 and subset['tech_comfort_score'].mean() < 4:
                phenotype_names[i] = 'Elderly Low-Tech'
            elif subset['readmission_risk_score'].mean() > 0.3:
                phenotype_names[i] = 'High-Risk Complex'
            elif subset['tech_comfort_score'].mean() > 6:
                phenotype_names[i] = 'Tech-Savvy Engaged'
            elif subset['health_literacy_score'].mean() < 2.5:
                phenotype_names[i] = 'Low-Literacy Support-Needed'
        
        data['phenotype_name'] = data['phenotype'].map(phenotype_names)
        
        self.phenotypes = phenotype_names
        return data
    
    def train_benefit_predictor(self,
                               data: pd.DataFrame,
                               target: str = 'would_benefit') -> Dict:
        """
        Train model to predict which patients would benefit from avatars
        
        Args:
            data: Patient data with features and outcomes
            target: Target variable name
            
        Returns:
            Model performance metrics
        """
        # Prepare features
        feature_cols = [
            'age', 'comorbidity_count', 'prior_admissions_12mo',
            'tech_comfort_score', 'has_smartphone', 'lives_alone',
            'english_primary_language', 'health_literacy_score',
            'readmission_risk_score', 'medication_count', 'adherence_score'
        ]
        
        X = data[feature_cols]
        y = data[target]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        
        # Train Random Forest
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            min_samples_leaf=20,
            random_state=42
        )
        rf_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred_proba = rf_model.predict_proba(X_test)[:, 1]
        y_pred = rf_model.predict(X_test)
        
        auc_score = roc_auc_score(y_test, y_pred_proba)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Confusion matrix
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        
        # Store model
        self.models['benefit_predictor'] = rf_model
        
        return {
            'auc_score': auc_score,
            'accuracy': (tp + tn) / (tp + tn + fp + fn),
            'precision': tp / (tp + fp) if (tp + fp) > 0 else 0,
            'recall': tp / (tp + fn) if (tp + fn) > 0 else 0,
            'feature_importance': feature_importance,
            'confusion_matrix': {
                'true_negative': int(tn),
                'false_positive': int(fp),
                'false_negative': int(fn),
                'true_positive': int(tp)
            }
        }
    
    def train_engagement_predictor(self,
                                  data: pd.DataFrame) -> Dict:
        """
        Train model to predict patient engagement levels
        
        Args:
            data: Patient data with engagement scores
            
        Returns:
            Model performance metrics
        """
        feature_cols = [
            'age', 'tech_comfort_score', 'has_smartphone',
            'english_primary_language', 'health_literacy_score',
            'lives_alone', 'prior_admissions_12mo'
        ]
        
        X = data[feature_cols]
        y = data['engagement_likelihood']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        
        # Train Gradient Boosting
        gb_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.1,
            random_state=42
        )
        gb_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = gb_model.predict(X_test)
        mse = np.mean((y_test - y_pred) ** 2)
        r2 = gb_model.score(X_test, y_test)
        
        # Store model
        self.models['engagement_predictor'] = gb_model
        
        return {
            'mse': mse,
            'rmse': np.sqrt(mse),
            'r2_score': r2,
            'mean_absolute_error': np.mean(np.abs(y_test - y_pred))
        }
    
    def generate_patient_scores(self, patient_data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate comprehensive scores for patient selection
        
        Args:
            patient_data: Patient features
            
        Returns:
            DataFrame with selection scores and recommendations
        """
        if 'benefit_predictor' not in self.models:
            raise ValueError("Models not trained. Run train_benefit_predictor first.")
        
        # Predict benefit probability
        feature_cols = [col for col in patient_data.columns 
                       if col not in ['patient_id', 'would_benefit', 'engagement_likelihood',
                                     'phenotype', 'phenotype_name']]
        
        benefit_prob = self.models['benefit_predictor'].predict_proba(
            patient_data[feature_cols[:11]]  # Use first 11 features
        )[:, 1]
        
        # Predict engagement
        engagement_features = [
            'age', 'tech_comfort_score', 'has_smartphone',
            'english_primary_language', 'health_literacy_score',
            'lives_alone', 'prior_admissions_12mo'
        ]
        engagement_score = self.models['engagement_predictor'].predict(
            patient_data[engagement_features]
        )
        
        # Calculate composite score
        composite_score = 0.6 * benefit_prob + 0.4 * engagement_score
        
        # Generate recommendations
        recommendations = []
        for i in range(len(patient_data)):
            if benefit_prob[i] > 0.7 and engagement_score[i] > 0.6:
                rec = 'Strong Candidate - High Priority'
            elif benefit_prob[i] > 0.5 and engagement_score[i] > 0.4:
                rec = 'Good Candidate - Standard Priority'
            elif benefit_prob[i] > 0.7 and engagement_score[i] < 0.4:
                rec = 'Would Benefit but Needs Engagement Support'
            elif engagement_score[i] > 0.6 and benefit_prob[i] < 0.3:
                rec = 'Engaged but Low Clinical Benefit'
            else:
                rec = 'Not Recommended - Consider Alternatives'
            recommendations.append(rec)
        
        # Determine best use case
        use_cases = []
        for i in range(len(patient_data)):
            if patient_data.iloc[i]['readmission_risk_score'] > 0.25:
                use_case = 'Discharge Education'
            elif patient_data.iloc[i]['medication_count'] > 7:
                use_case = 'Medication Adherence'
            elif patient_data.iloc[i]['health_literacy_score'] < 2.5:
                use_case = 'Health Education'
            else:
                use_case = 'General Support'
            use_cases.append(use_case)
        
        results = patient_data.copy()
        results['benefit_probability'] = benefit_prob
        results['engagement_score'] = engagement_score
        results['composite_score'] = composite_score
        results['recommendation'] = recommendations
        results['suggested_use_case'] = use_cases
        
        return results.sort_values('composite_score', ascending=False)


def demonstrate_patient_selection():
    """Demonstrate ML patient selection framework"""
    selector = MLPatientSelector()
    
    print("="*60)
    print("ML-BASED PATIENT SELECTION FOR AVATAR INTERVENTIONS")
    print("="*60)
    
    # 1. Generate synthetic data
    print("\n1. Generating Synthetic Patient Data...")
    data = selector.create_patient_features(n_patients=1000)
    print(f"   Created {len(data)} patient records")
    
    # 2. Identify phenotypes
    print("\n2. Identifying Patient Phenotypes...")
    data = selector.identify_patient_phenotypes(data, n_clusters=4)
    print("\n   Phenotype Distribution:")
    for phenotype, count in data['phenotype_name'].value_counts().items():
        print(f"   - {phenotype}: {count} patients ({count/len(data)*100:.1f}%)")
    
    # 3. Train benefit predictor
    print("\n3. Training Benefit Prediction Model...")
    benefit_metrics = selector.train_benefit_predictor(data)
    print(f"   AUC Score: {benefit_metrics['auc_score']:.3f}")
    print(f"   Accuracy: {benefit_metrics['accuracy']:.3f}")
    print(f"   Precision: {benefit_metrics['precision']:.3f}")
    print(f"   Recall: {benefit_metrics['recall']:.3f}")
    
    print("\n   Top Feature Importances:")
    for _, row in benefit_metrics['feature_importance'].head(5).iterrows():
        print(f"   - {row['feature']}: {row['importance']:.3f}")
    
    # 4. Train engagement predictor
    print("\n4. Training Engagement Prediction Model...")
    engagement_metrics = selector.train_engagement_predictor(data)
    print(f"   R² Score: {engagement_metrics['r2_score']:.3f}")
    print(f"   RMSE: {engagement_metrics['rmse']:.3f}")
    
    # 5. Generate patient scores
    print("\n5. Generating Patient Selection Scores...")
    scored_patients = selector.generate_patient_scores(data.head(100))
    
    print("\n   Top 5 Candidates:")
    top_candidates = scored_patients.head(5)[
        ['patient_id', 'composite_score', 'recommendation', 'suggested_use_case']
    ]
    for _, patient in top_candidates.iterrows():
        print(f"   {patient['patient_id']}: Score={patient['composite_score']:.3f}, "
              f"{patient['recommendation']}, Use Case: {patient['suggested_use_case']}")
    
    print("\n   Recommendation Distribution:")
    for rec, count in scored_patients['recommendation'].value_counts().items():
        print(f"   - {rec}: {count} patients")
    
    return selector, scored_patients


if __name__ == '__main__':
    selector, results = demonstrate_patient_selection()
    
    # Optional: Save results
    # results.to_csv('patient_selection_scores.csv', index=False)
    print("\n✓ Patient selection complete")