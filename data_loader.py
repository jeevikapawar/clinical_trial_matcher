import pandas as pd
import logging 
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class PatientDataLoader:
    def __init__(self, data_dir: str):
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path(data_dir)
        self.patients_data = self._load_patient_data()
        self.logger.info(f"Loaded {len(self.patients_data)} patient records")
    def _load_patient_data(self) -> Dict[str, Dict[str, Any]]:
        self.logger.info(f"Loading patient data from {self.data_dir}")
        patients_data = {}
        csv_files = list(self.data_dir.glob('*.csv'))
        
        if not csv_files:
            self.logger.warning(f"No CSV files found in {self.data_dir}")
            return patients_data

        # Load patients.csv first
        patients_file = next((f for f in csv_files if f.name == 'patients.csv'), None)
        if patients_file:
            try:
                patients_df = pd.read_csv(patients_file)
                for _, row in patients_df.iterrows():
                    patient_id = str(row['Id'])
                    birthdate = pd.to_datetime(row['BIRTHDATE'])
                    deathdate = pd.to_datetime(row['DEATHDATE']) if pd.notna(row['DEATHDATE']) else None
                    patients_data[patient_id] = {
                        'age': self._calculate_age(birthdate, deathdate),
                        'gender': row['GENDER'],
                        'condition_codes': [],
                        'medication_codes': [],
                    }
            except Exception as e:
                self.logger.error(f"Error parsing {patients_file}: {str(e)}")

        
        for csv_file in csv_files:
            if csv_file.name == 'patients.csv':
                continue  # Already processed
            try:
                df = pd.read_csv(csv_file)
                if 'PATIENT' in df.columns:
                    self._process_patient_related_file(df, patients_data, csv_file.stem)
            except Exception as e:
                self.logger.error(f"Error parsing {csv_file}: {str(e)}")

        self.logger.info(f"Loaded data for {len(patients_data)} patients")
        return patients_data

    def _process_patient_related_file(self, df: pd.DataFrame, patients_data: Dict[str, Dict[str, Any]], file_type: str):
        for _, row in df.iterrows():
            patient_id = str(row['PATIENT'])
            if patient_id in patients_data:
                if file_type == 'conditions':
                    patients_data[patient_id]['condition_codes'].append(row['CODE'])
                elif file_type == 'medications':
                    patients_data[patient_id]['medication_codes'].append(row['CODE'])
                

    def _calculate_age(self, birthdate: pd.Timestamp, deathdate: Optional[pd.Timestamp] = None) -> int:
        end_date = deathdate if deathdate else pd.Timestamp.now()
        age = end_date.year - birthdate.year
        if end_date.month < birthdate.month or (end_date.month == birthdate.month and end_date.day < birthdate.day):
            age -= 1
        return max(0, age)  

    def get_patients_dataframe(self) -> pd.DataFrame:
        if not self.patients_data:
            raise ValueError("Patient data has not been loaded.")
        
        df = pd.DataFrame.from_dict(self.patients_data, orient='index')
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'patient_id'}, inplace=True)
        return df