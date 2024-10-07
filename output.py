# src/output_generator.py
import json
import pandas as pd
from typing import Dict, List
from pathlib import Path
from datetime import datetime

class OutputGenerator:
    def __init__(self, output_directory: str):
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)

    def generate_outputs(self, matches: Dict[str, List[Dict]]) -> tuple:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_path = self._save_json(matches, timestamp)
        excel_path = self._save_excel(matches, timestamp)
        
        return json_path, excel_path

    def _save_json(self, matches: Dict[str, List[Dict]], timestamp: str) -> Path:
        output_path = self.output_directory / f'trial_matches_{timestamp}.json'
        
        formatted_data = {
            'matches': [
                {
                    'patientId': patient_id,
                    'eligibleTrials': trials
                }
                for patient_id, trials in matches.items()
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(formatted_data, f, indent=2)
            
        return output_path

    def _save_excel(self, matches: Dict[str, List[Dict]], timestamp: str) -> Path:
        """Save matches to an Excel file with multiple sheets."""
        output_path = self.output_directory / f'trial_matches_{timestamp}.xlsx'
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            self._create_summary_sheet(matches, writer)
            self._create_detailed_matches_sheet(matches, writer)
            self._create_criteria_sheet(matches, writer)
        return output_path

    def _create_summary_sheet(self, matches: Dict[str, List[Dict]], 
                            writer: pd.ExcelWriter) -> None:
        summary_data = {
            'Patient ID': [],
            'Number of Eligible Trials': [],
            'Trial IDs': []
        }
        
        for patient_id, trials in matches.items():
            summary_data['Patient ID'].append(patient_id)
            summary_data['Number of Eligible Trials'].append(len(trials))
            summary_data['Trial IDs'].append(
                ', '.join(trial['trialId'] for trial in trials)
            )
            
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

    def _create_detailed_matches_sheet(self, matches: Dict[str, List[Dict]], 
                                     writer: pd.ExcelWriter) -> None:
        detailed_data = {
            'Patient ID': [],
            'Trial ID': [],
            'Trial Name': [],
            'Number of Criteria Met': []
        }
        
        for patient_id, trials in matches.items():
            for trial in trials:
                detailed_data['Patient ID'].append(patient_id)
                detailed_data['Trial ID'].append(trial['trialId'])
                detailed_data['Trial Name'].append(trial['trialName'])
                detailed_data['Number of Criteria Met'].append(
                    len(trial['eligibilityCriteriaMet'])
                )
                
        detailed_df = pd.DataFrame(detailed_data)
        detailed_df.to_excel(writer, sheet_name='Detailed Matches', index=False)

    def _create_criteria_sheet(self, matches: Dict[str, List[Dict]], 
                             writer: pd.ExcelWriter) -> None:
        criteria_data = {
            'Patient ID': [],
            'Trial ID': [],
            'Criterion': []
        }
        
        for patient_id, trials in matches.items():
            for trial in trials:
                for criterion in trial['eligibilityCriteriaMet']:
                    criteria_data['Patient ID'].append(patient_id)
                    criteria_data['Trial ID'].append(trial['trialId'])
                    criteria_data['Criterion'].append(criterion)
                    
        criteria_df = pd.DataFrame(criteria_data)
        criteria_df.to_excel(writer, sheet_name='Matching Criteria', index=False)