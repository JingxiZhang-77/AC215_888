"""
Classification Service

Business logic for safety event classification using LLM-based analysis.
Integrates with the model service for prompt-based classification.
"""

import sys
import os
from typing import Dict, Any, List, Tuple
import pandas as pd
from datetime import datetime
import traceback

# Add model directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'model'))

try:
    from simple_prompt_utils import (
        prompt1_single_incident,
        prompt2_single_incident,
        prompt3_single_incident
    )
    PROMPT_UTILS_AVAILABLE = True
except ImportError:
    PROMPT_UTILS_AVAILABLE = False
    print("Warning: simple_prompt_utils not available")

from utils.logger import logger
from utils.config import settings


class ClassificationService:
    """
    Service for classifying safety events using AI-powered analysis
    
    Implements the three-step classification process:
    1. GAPS deviation check
    2. Reached patient check  
    3. Harm level assessment
    """
    
    def __init__(self):
        """Initialize classification service"""
        self.valid_departments = settings.VALID_DEPARTMENTS
        logger.info("Classification service initialized")
    
    def classify_incident(
        self, 
        description: str, 
        department: str = None
    ) -> Dict[str, Any]:
        """
        Classify a single safety incident
        
        Args:
            description: Incident description text
            department: Optional department name
            
        Returns:
            Dictionary with classification results and rationales
        """
        if not PROMPT_UTILS_AVAILABLE:
            return self._mock_classification(description, department)
        
        # Validate and normalize department
        if department:
            department = department.lower().strip()
            if department not in self.valid_departments:
                logger.warning(f"Invalid department: {department}, setting to unspecified")
                department = "unspecified"
        else:
            department = "unspecified"
        
        # Initialize result structure
        result = {
            "incident": description,
            "department": department,
            "gaps_deviation_check": 'N/A',
            "gaps_rationale": 'N/A',
            "reached_patient_check": 'N/A',
            "reached_patient_rationale": 'N/A',
            "harm_level_check": 'N/A',
            "harm_level_rationale": 'N/A',
            "final_classification_code": 'Unknown',
            "final_rationale": 'N/A',
            "status": "success",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Step 1: GAPS deviation check
            logger.info(f"Step 1: Checking GAPS deviation for incident")
            gaps_deviation_bool, gaps_rationale = prompt1_single_incident(description)
            result["gaps_deviation_check"] = "Yes" if gaps_deviation_bool else "No"
            result["gaps_rationale"] = gaps_rationale
            
            if not gaps_deviation_bool:
                result["final_classification_code"] = "NSE"
                result["final_rationale"] = (
                    f"No deviation from Generally Accepted Performance Standards (GAPS). "
                    f"{gaps_rationale}"
                )
                logger.info("Classification: NSE (No deviation)")
                return result
            
            # Step 2: Reached patient check
            logger.info(f"Step 2: Checking if incident reached patient")
            reached_patient_bool, reached_patient_rationale = prompt2_single_incident(description)
            result["reached_patient_check"] = "Yes" if reached_patient_bool else "No"
            result["reached_patient_rationale"] = reached_patient_rationale
            
            if not reached_patient_bool:
                result["final_classification_code"] = "NME"
                result["final_rationale"] = (
                    f"Deviation occurred but did not reach the patient. "
                    f"{reached_patient_rationale}"
                )
                logger.info("Classification: NME (No patient reach)")
                return result
            
            # Step 3: Harm level assessment
            logger.info(f"Step 3: Assessing harm level")
            harm_bool, harm_rationale = prompt3_single_incident(description)
            result["harm_level_check"] = "Yes" if harm_bool else "No"
            result["harm_level_rationale"] = harm_rationale
            
            if harm_bool:
                result["final_classification_code"] = "HE"
                result["final_rationale"] = (
                    f"Harmful event - patient experienced harm. {harm_rationale}"
                )
                logger.info("Classification: HE (Harmful event)")
            else:
                result["final_classification_code"] = "NHE"
                result["final_rationale"] = (
                    f"No harm event - reached patient but no harm resulted. "
                    f"{harm_rationale}"
                )
                logger.info("Classification: NHE (No harm)")
            
            return result
            
        except Exception as e:
            logger.error(f"Classification error: {e}")
            logger.error(traceback.format_exc())
            result["status"] = "error"
            result["final_rationale"] = f"Error during classification: {type(e).__name__}: {str(e)}"
            return result
    
    def classify_batch(
        self, 
        incidents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Classify multiple incidents
        
        Args:
            incidents: List of incident dictionaries with 'description' and optional 'department'
            
        Returns:
            List of classification results
        """
        results = []
        
        for idx, incident in enumerate(incidents):
            logger.info(f"Classifying incident {idx + 1}/{len(incidents)}")
            
            description = incident.get('description', '').strip()
            department = incident.get('department', None)
            
            if not description:
                logger.warning(f"Skipping incident {idx + 1}: empty description")
                continue
            
            result = self.classify_incident(description, department)
            results.append(result)
        
        logger.info(f"Batch classification complete: {len(results)} incidents processed")
        return results
    
    def process_file(
        self, 
        file_path: str
    ) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """
        Process CSV or Excel file containing incidents
        
        Args:
            file_path: Path to input file
            
        Returns:
            Tuple of (results list, department statistics dict)
        """
        try:
            # Read file
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            
            logger.info(f"Loaded file with {len(df)} rows")
            
            # Find description column
            description_col = None
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['description', 'incident', 'event', 'brief']):
                    description_col = col
                    break
            
            if description_col is None:
                description_col = df.columns[0]
                logger.warning(f"No description column found, using first column: {description_col}")
            
            # Find department column
            department_col = None
            for col in df.columns:
                if 'department' in col.lower():
                    department_col = col
                    logger.info(f"Found department column: {department_col}")
                    break
            
            # Process incidents
            incidents = []
            for idx, row in df.iterrows():
                description = str(row[description_col])
                
                if description and description.strip() and description.lower() != 'nan':
                    incident = {'description': description.strip()}
                    
                    # Add department if available
                    if department_col and department_col in row.index:
                        dept_value = str(row[department_col])
                        if dept_value and dept_value.strip() and dept_value.lower() != 'nan':
                            incident['department'] = dept_value.strip()
                    
                    incidents.append(incident)
            
            # Classify all incidents
            results = self.classify_batch(incidents)
            
            # Calculate department statistics
            dept_stats = {}
            for result in results:
                dept = result.get('department', 'unspecified')
                dept_stats[dept] = dept_stats.get(dept, 0) + 1
            
            return results, dept_stats
            
        except Exception as e:
            logger.error(f"File processing error: {e}")
            raise
    
    def _mock_classification(
        self, 
        description: str, 
        department: str = None
    ) -> Dict[str, Any]:
        """
        Mock classification for testing when prompt utils unavailable
        
        Args:
            description: Incident description
            department: Optional department
            
        Returns:
            Mock classification result
        """
        return {
            "incident": description,
            "department": department or "unspecified",
            "gaps_deviation_check": "Yes",
            "gaps_rationale": "Mock rationale - prompt utils not available",
            "reached_patient_check": "Yes",
            "reached_patient_rationale": "Mock rationale",
            "harm_level_check": "No",
            "harm_level_rationale": "Mock rationale",
            "final_classification_code": "NHE",
            "final_rationale": "Mock classification result",
            "status": "success",
            "timestamp": datetime.utcnow().isoformat()
        }


# Global service instance
classification_service = ClassificationService()
