# src/matcher.py
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime
from src.data_loader import PatientDataLoader
from src.trial_scraper import TrialScraper

class TrialMatcher:
    def __init__(self, patient_loader: PatientDataLoader, trial_scraper: TrialScraper):
        self.patient_loader = patient_loader
        self.trial_scraper = trial_scraper
        self.matches = {}

    def match_all_patients(self) -> Dict[str, List[Dict]]:
        print("Initiating Matcher")
        patients_df = self.patient_loader.get_patients_dataframe()
        print(f"Loaded {len(patients_df)} patient records")
        print("Fetching active trials")
        active_trials = self.trial_scraper.get_active_trials()
        print(f"Fetched {len(active_trials)} active trials")
        print("Matcher looping through patients")
        
        for _, patient in patients_df.iterrows():
            eligible_trials = []
            
            for trial in active_trials:
                eligibility_criteria_met = self._check_eligibility(patient, trial)
                
                if eligibility_criteria_met:
                    eligible_trials.append({
                        'trialId': trial['trial_id'],
                        'trialName': trial['trial_name'],
                        'eligibilityCriteriaMet': eligibility_criteria_met
                    })
            
            self.matches[patient['patient_id']] = eligible_trials
        print(f"Matching completed. {len(self.matches)} patients processed.")    
        return self.matches

    def _check_eligibility(self, patient: pd.Series, trial: Dict) -> Optional[List[str]]:
        criteria_met = []
        if not self._check_age_criteria(patient['age'], trial):
            return None
        criteria_met.append(f"Age {patient['age']} within trial limits: {trial['minimum_age']}-{trial['maximum_age']}")
        
        if not self._check_gender_criteria(patient['gender'], trial):
            return None
        criteria_met.append(f"Gender {patient['gender']} matches trial requirements")
        condition_match = self._check_condition_criteria(patient['condition_codes'], trial)
        if not condition_match:
            return None
        criteria_met.extend(condition_match)
        exclusion_violated = self._check_exclusion_criteria(
            patient['condition_codes'], 
            patient['medication_codes'],
            trial
        )
        if exclusion_violated:
            return None
        criteria_met.append("No exclusion criteria violated")
        lab_criteria = self._check_lab_criteria(patient['recent_lab_results'], trial)
        if lab_criteria:
            criteria_met.extend(lab_criteria)
        
        return criteria_met

    def _check_age_criteria(self, patient_age: float, trial: Dict) -> bool:
        """Check if patient meets the age requirements for the trial."""
        min_age = trial.get('minimum_age', 0)
        max_age = trial.get('maximum_age', 150)
        
        return min_age <= patient_age <= max_age

    def _check_gender_criteria(self, patient_gender: str, trial: Dict) -> bool:
        trial_gender = trial.get('gender', 'All')
        
        if trial_gender == 'All':
            return True
            
        return patient_gender.lower() == trial_gender.lower()

    def _check_condition_criteria(self, patient_conditions: List[str], trial: Dict) -> Optional[List[str]]:
        trial_conditions = trial.get('conditions', [])
        matching_conditions = []
        
        # Convert all conditions to lowercase for comparison
        patient_conditions_lower = [c.lower() for c in patient_conditions]
        trial_conditions_lower = [c.lower() for c in trial_conditions]
        
        for trial_condition in trial_conditions_lower:
            if any(self._condition_matches(trial_condition, pc) for pc in patient_conditions_lower):
                matching_conditions.append(f"Matches trial condition: {trial_condition}")
                
        return matching_conditions if matching_conditions else None

    def _condition_matches(self, trial_condition: str, patient_condition: str) -> bool:
        if trial_condition == patient_condition:
            return True
            
        if trial_condition in patient_condition or patient_condition in trial_condition:
            return True
            
        return False

    def _check_exclusion_criteria(self, patient_conditions: List[str], 
                                patient_medications: List[str], 
                                trial: Dict) -> bool:
 
        exclusion_criteria = trial.get('exclusion_criteria', [])
        
        for criterion in exclusion_criteria:
            criterion_lower = criterion.lower()

            for condition in patient_conditions:
                if condition.lower() in criterion_lower:
                    return True
                    
            for medication in patient_medications:
                if medication.lower() in criterion_lower:
                    return True
                    
        return False

    def _check_lab_criteria(self, patient_labs: Dict[str, float], trial: Dict) -> List[str]:
        
        matching_criteria = []
        
       
        lab_criteria = self._extract_lab_criteria(trial.get('inclusion_criteria', []))
        
        for lab_code, (min_value, max_value) in lab_criteria.items():
            if lab_code in patient_labs:
                lab_value = patient_labs[lab_code]
                if min_value <= lab_value <= max_value:
                    matching_criteria.append(
                        f"Lab result {lab_code}: {lab_value} within required range: {min_value}-{max_value}"
                    )
                    
        return matching_criteria

    def _extract_lab_criteria(self, inclusion_criteria: List[str]) -> Dict[str, tuple]:
        
        lab_criteria = {}
        
       
        for criterion in inclusion_criteria:
            if any(lab_keyword in criterion.lower() for lab_keyword in ['lab', 'test', 'level']):
 
                pass
                
        return lab_criteria