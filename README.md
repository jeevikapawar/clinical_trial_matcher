Clinical Trial Matcher

## Project Overview

This project develops a matching algorithm that takes patient data as input and outputs a list of clinical trials that each patient is eligible for. The algorithm matches patient data from Synthea with actively recruiting clinical trials from ClinicalTrials.gov.

## Features

- Load and process patient data from Synthea
- Scrape and parse clinical trial data from ClinicalTrials.gov
- Match patients to eligible clinical trials based on inclusion/exclusion criteria
- Generate output in JSON and Excel formats

## Prerequisites

- Python 3.7+
- pip (Python package installer)
- pandas
- requests
- beautifulsoup

## Installation

1. Clone the repository:
   git clone https://github.com/yourusername/clinical_trial_matcher.git
   cd clinical_trial_matcher

2. Create and activate a virtual environment:
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   

3. Install the required packages: pip install -r requirements.txt
   

## Usage

1. Ensure you have downloaded the Synthea patient data and placed it in the appropriate directory (default: `data/raw/synthea_sample_data_csv_latest`).

2. Run the main script: PYTHONPATH=/path/to/project python3 src/main.py --data-dir "/path/to/synthea/data"
   Note: Replace `/path/to/project` with the actual path to your project directory, and `/path/to/synthea/data` with the path to your Synthea data.

3. The script will process the data and generate output files in the `data/processed` directory.

## Output

The script generates two output files:
1. A JSON file containing the list of eligible trials for each patient.
2. An Excel file with the same information in a tabular format.

The output format for each patient is:
json
{
  "patientId": "string",
  "eligibleTrials": [
    {
      "trialId": "string",
      "trialName": "string",
      "eligibilityCriteriaMet": ["string"]
    }
  ]
}

## Acknowledgments

- Synthea for providing synthetic patient data
- ClinicalTrials.gov for providing access to clinical trial information
