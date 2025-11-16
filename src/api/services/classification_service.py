"""
Classification Service

Business logic for safety event classification using LLM-based analysis.
Integrates with the model service for prompt-based classification.
"""

import sys
import os
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
from datetime import datetime
import traceback

# Add model directory to path (supports running from repo root, src/api, or Docker)
MODEL_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "model"
    )
)

if os.path.isdir(MODEL_DIR) and MODEL_DIR not in sys.path:
    sys.path.append(MODEL_DIR)
else:
    print(f"Warning: model directory not found at {MODEL_DIR}")

try:
    from simple_prompt_utils import (
        prompt1_single_incident,
        prompt2_single_incident,
        prompt3_single_incident
    )
    PROMPT_UTILS_AVAILABLE = True
except ImportError as exc:
    PROMPT_UTILS_AVAILABLE = False
    print(f"Warning: simple_prompt_utils not available ({exc})")

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
        self.department_lookup = {
            self._normalize_key(dept): dept
            for dept in settings.VALID_DEPARTMENTS
        }
        # allow unspecified to pass through normalization
        self.department_lookup["unspecified"] = "unspecified"
        self.default_department = "unspecified"
        self.department_labels = {
            "internal medicine": "Internal Medicine",
            "surgery": "Surgery",
            "ob/gyn/nicu": "OB/GYN/NICU",
            "radiology/imaging": "Radiology/Imaging",
            "outpatient/ER": "Outpatient/ER",
            "unspecified": "Unspecified"
        }
        self.department_slugs = {
            "internal medicine": "internal_medicine",
            "surgery": "surgery",
            "ob/gyn/nicu": "ob_gyn_nicu",
            "radiology/imaging": "radiology_imaging",
            "outpatient/ER": "outpatient_er",
            "unspecified": "unspecified"
        }
        self.classification_labels = {
            "SSE": "Serious Safety Event",
            "PSE": "Precursor Safety Event",
            "NME": "Near Miss Event",
            "NSE": "No Safety Event"
        }
        logger.info("Classification service initialized")

    @staticmethod
    def _normalize_key(value: str) -> str:
        """Normalize department identifiers for comparison"""
        if not isinstance(value, str):
            return ""
        normalized = value.strip().lower()
        for char in ['_', '-', '/']:
            normalized = normalized.replace(char, ' ')
        return ' '.join(normalized.split())

    def _normalize_department(self, department: Optional[str]) -> str:
        """
        Convert user-provided department strings (slugged, spaced, etc.)
        into canonical names expected by the LLM prompts.
        """
        if not department:
            return self.default_department
        normalized_key = self._normalize_key(department)
        canonical = self.department_lookup.get(normalized_key)
        if canonical:
            return canonical
        logger.warning(f"Invalid department: {department}. Defaulting to unspecified.")
        return self.default_department

    def _format_department_label(self, department: str) -> str:
        return self.department_labels.get(department, department.title())

    def _department_slug(self, department: str) -> Optional[str]:
        return self.department_slugs.get(department)

    def _build_base_result(self, description: str, department: str) -> Dict[str, Any]:
        department_label = self._format_department_label(department)
        return {
            "incident": description,
            "department": department,
            "department_label": department_label,
            "department_slug": self._department_slug(department),
            "deviation_check": "N/A",
            "deviation_rationale": "N/A",
            "patient_reach_check": "N/A",
            "patient_reach_rationale": "N/A",
            "harm_level_check": "N/A",
            "harm_level_rationale": "N/A",
            "classification_code": "Unknown",
            "classification_label": "Unknown",
            "classification_rationale": "N/A",
            "status": "success",
            "timestamp": datetime.utcnow().isoformat()
        }
    
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
        department = self._normalize_department(department)
        
        # Initialize result structure
        result = self._build_base_result(description, department)
        prompt_department = result["department_label"] if department != self.default_department else None
        
        try:
            # Step 1: GAPS deviation check
            logger.info(f"Step 1: Checking GAPS deviation for incident")
            gaps_deviation_bool, gaps_rationale = prompt1_single_incident(description, prompt_department)
            result["deviation_check"] = "Yes" if gaps_deviation_bool else "No"
            result["deviation_rationale"] = gaps_rationale
            
            if not gaps_deviation_bool:
                result["classification_code"] = "NSE"
                result["classification_label"] = self.classification_labels["NSE"]
                result["classification_rationale"] = (
                    f"No deviation from Generally Accepted Performance Standards (GAPS). "
                    f"{gaps_rationale}"
                )
                logger.info("Classification: NSE (No deviation)")
                self._attach_legacy_fields(result)
                return result
            
            # Step 2: Reached patient check
            logger.info(f"Step 2: Checking if incident reached patient")
            reached_patient_bool, reached_patient_rationale = prompt2_single_incident(description, prompt_department)
            result["patient_reach_check"] = "Yes" if reached_patient_bool else "No"
            result["patient_reach_rationale"] = reached_patient_rationale
            
            if not reached_patient_bool:
                result["classification_code"] = "NME"
                result["classification_label"] = self.classification_labels["NME"]
                result["classification_rationale"] = (
                    f"Deviation occurred but did not reach the patient. "
                    f"{reached_patient_rationale}"
                )
                logger.info("Classification: NME (No patient reach)")
                self._attach_legacy_fields(result)
                return result
            
            # Step 3: Harm level assessment
            logger.info(f"Step 3: Assessing harm level")
            harm_bool, harm_rationale = prompt3_single_incident(description, prompt_department)
            result["harm_level_check"] = "Yes" if harm_bool else "No"
            result["harm_level_rationale"] = harm_rationale
            
            if harm_bool:
                result["classification_code"] = "SSE"
                result["classification_label"] = self.classification_labels["SSE"]
                result["classification_rationale"] = (
                    f"Serious Safety Event - deviation reached the patient and caused moderate/severe harm or death. {harm_rationale}"
                )
                logger.info("Classification: SSE (Serious Safety Event)")
            else:
                result["classification_code"] = "PSE"
                result["classification_label"] = self.classification_labels["PSE"]
                result["classification_rationale"] = (
                    f"Precursor Safety Event - deviation reached the patient with no or minimal harm. "
                    f"{harm_rationale}"
                )
                logger.info("Classification: PSE (Precursor Safety Event)")
            
            self._attach_legacy_fields(result)
            return result
            
        except Exception as e:
            logger.error(f"Classification error: {e}")
            logger.error(traceback.format_exc())
            result["status"] = "error"
            result["classification_rationale"] = f"Error during classification: {type(e).__name__}: {str(e)}"
            self._attach_legacy_fields(result)
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
        normalized_department = self._normalize_department(department)
        result = self._build_base_result(description, normalized_department)
        result["deviation_check"] = "Yes"
        result["deviation_rationale"] = "Mock rationale - prompt utils not available"
        result["patient_reach_check"] = "Yes"
        result["patient_reach_rationale"] = "Mock rationale"
        result["harm_level_check"] = "No"
        result["harm_level_rationale"] = "Mock rationale"
        result["classification_code"] = "PSE"
        result["classification_label"] = self.classification_labels["PSE"]
        result["classification_rationale"] = "Mock classification result"
        self._attach_legacy_fields(result)
        return result

    def _attach_legacy_fields(self, result: Dict[str, Any]) -> None:
        """
        Populate the legacy response fields so older clients continue working.
        """
        result["gaps_deviation_check"] = result.get("deviation_check")
        result["gaps_rationale"] = result.get("deviation_rationale")
        result["reached_patient_check"] = result.get("patient_reach_check")
        result["reached_patient_rationale"] = result.get("patient_reach_rationale")
        result["final_classification_code"] = result.get("classification_code")
        result["final_rationale"] = result.get("classification_rationale")


# Global service instance
classification_service = ClassificationService()
