import requests
import xml.etree.ElementTree as ET
import logging

class TrialScraper:
    def __init__(self):
        self.base_url = "https://clinicaltrials.gov/"
        self.logger = logging.getLogger(__name__)
    def get_active_trials(self):
        params = {
        "status":"Recruiting",
        "fields": "NCTId,BriefTitle,EligibilityCriteria,Gender,MinimumAge,MaximumAge,OverallStatus,Condition",
        "fmt": "xml",
        "max_rnk": 100
        }
        print("API request URL:", self.base_url)
        print("API request parameters:", params)
        response = requests.get(self.base_url, params=params)
        logging.info(f"Response content: {response.content.decode('utf-8')[:500]}")  # Log first 500 characters

        if response.status_code != 200:
            self.logger.error(f"API request failed with status code {response.status_code}")
            return []
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse XML: {str(e)}")
            return []
        trials = []
        
        for clinical_study in root.findall('clinical_study'):
            trial = self._parse_trial_data(clinical_study)
            if trial:
                trials.append(trial)

        return trials

    def _parse_trial_data(self, clinical_study):
        trial = {
            'trial_id': self._get_text(clinical_study, 'nct_id'),
            'trial_name': self._get_text(clinical_study, 'brief_title'),
            'status': self._get_text(clinical_study, 'overall_status'),
            'phase': self._get_text(clinical_study, 'phase'),
            'conditions': [cond.text for cond in clinical_study.findall('.//condition')],
            'inclusion_criteria': self._parse_criteria(clinical_study, 'inclusion'),
            'exclusion_criteria': self._parse_criteria(clinical_study, 'exclusion'),
            'minimum_age': self._parse_age(self._get_text(clinical_study, 'minimum_age')),
            'maximum_age': self._parse_age(self._get_text(clinical_study, 'maximum_age')),
            'gender': self._get_text(clinical_study, 'gender'),
            'healthy_volunteers': self._get_text(clinical_study, 'healthy_volunteers') == 'Accepts Healthy Volunteers'
        }

        return trial if trial['trial_id'] else None

    def _get_text(self, element, tag):
        elem = element.find(tag)
        return elem.text if elem is not None else None

    def _parse_criteria(self, clinical_study, criteria_type):
        criteria = []
        criteria_elem = clinical_study.find(f'{criteria_type}_criteria')
        if criteria_elem is not None:
            for textblock in criteria_elem.findall('textblock'):
                criteria.extend([line.strip() for line in textblock.text.split('\n') if line.strip()])
        return criteria

    def _parse_age(self, age_str):
        if not age_str:
            return None
        try:
            age = float(age_str.split()[0])
            if 'Month' in age_str:
                age /= 12  
            return age
        except (ValueError, IndexError):
            return None
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = TrialScraper()
    active_trials = scraper.get_active_trials()
    for trial in active_trials:
        print(trial)
