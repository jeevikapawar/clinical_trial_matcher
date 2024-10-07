import logging
import os
import time
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass
from data_loader import PatientDataLoader
from src.data_loader import PatientDataLoader
from src.output import OutputGenerator
from src.matcher import TrialMatcher
from src.trial_scraper import TrialScraper

@dataclass
class PipelineConfig:
    data_dir: str
    output_dir: str
    #criteria_file: str
    config_file: Optional[str] = None
    dry_run: bool = False


        
class MatchingPipeline: 
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

    def setup_logging(verbose: bool = False):
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def validate_directories(self) -> None:
        
        self.logger.info("Validating directories...")
        
        data_path = Path(self.config.data_dir)
        output_path = Path(self.config.output_dir)
        
        if not data_path.exists():
            raise ValueError(f"Data directory does not exist: {self.config.data_dir}")
        
        if not data_path.is_dir():
            raise ValueError(f"Data path is not a directory: {self.config.data_dir}")
        
        
        output_path.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Output directory ready: {output_path}")
        csv_files = list(data_path.glob('*.csv'))
        #xml_files = list(data_path.glob('*.xml'))
        
        if not csv_files:
            raise ValueError(f"No CSV files found in data directory: {data_path}")

    

    def generate_summary_stats(self, matches: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'total_patients': len(matches),
            'matched_patients': sum(1 for m in matches.values() if m),
            'match_rate': f"{(sum(1 for m in matches.values() if m) / len(matches)) * 100:.1f}%"
        }

    def run(self) -> Tuple[Optional[Path], Optional[Path]]:
        start_time = time.time()
        self.logger.info("Starting clinical trial matching pipeline...")
        
        try:
            self.validate_directories()
            self.logger.info("Initializing pipeline components...")
            patient_loader = PatientDataLoader(self.config.data_dir)
            trial_scraper = TrialScraper()
            
            trial_matcher = TrialMatcher(
                patient_loader=patient_loader,
                trial_scraper=trial_scraper,
            )
           
            self.logger.info(f"Processing {len(patient_loader.patients_data)} patient records...")
            matches = trial_matcher.match_all_patients()
            
            
            stats = self.generate_summary_stats(matches)
            self.logger.info("Matching Summary:")
            for key, value in stats.items():
                self.logger.info(f"  {key}: {value}")
            
            if self.config.dry_run:
                self.logger.info("Dry run completed successfully")
                return None, None
         
            output_generator = OutputGenerator(self.config.output_dir)
            json_path, excel_path = output_generator.generate_outputs(matches)
            
            execution_time = time.time() - start_time
            self.logger.info(
                f"Pipeline completed in {execution_time:.2f} seconds\n"
                f"Results saved to:\n"
                f"  JSON: {json_path}\n"
                f"  Excel: {excel_path}"
            )
            
            return json_path, excel_path
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            raise
    
    

def main():
    try:
        config = PipelineConfig(
            data_dir="/Users/jeevikapawar/Documents/clinical_trial_matcher/data/raw/synthea_sample_data_csv_latest",
            output_dir="/Users/jeevikapawar/Documents/clinical_trial_matcher/data/processed",
            #criteria_file="/Users/jeevikapawar/Documents/Clinical Trial Matcher/config/criteria.json"
        )
        
        pipeline = MatchingPipeline(config)
        pipeline.run()
        
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()