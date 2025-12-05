# Safety Event Classification System - Reference Guide

## Classification Logic

The system uses a **3-step decision tree** to classify safety incidents into 4 categories.

### Decision Tree Flow

```
START
  ↓
[Step 1] Did deviation from GAPS occur?
  ↓ NO  → NSE (No Safety Event)
  ↓ YES
  ↓
[Step 2] Did deviation reach the patient?
  ↓ NO  → NME (Near Miss Event)
  ↓ YES
  ↓
[Step 3] Did patient experience harm?
  ↓ NO  → PSE (Precursor Safety Event)
  ↓ YES
  ↓
SSE (Serious Safety Event)
```

---

## Classification Codes

**Ranked by descending level of seriousness:**

### 1. SSE - Serious Safety Event 🔴
- **Definition**: Deviation reached the patient and caused moderate/severe harm or death
- **Criteria**:
  - ✅ Deviation from GAPS occurred
  - ✅ Deviation reached the patient
  - ✅ Patient experienced moderate/severe harm or death
- **Examples**:
  - Surgical error resulting in permanent injury
  - Medication error causing severe allergic reaction
  - Fall resulting in broken bones or head injury

### 2. PSE - Precursor Safety Event 🟡
- **Definition**: Deviation reached the patient with no or minimal harm
- **Criteria**:
  - ✅ Deviation from GAPS occurred
  - ✅ Deviation reached the patient
  - ❌ No harm or only minimal harm occurred
- **Examples**:
  - Patient received wrong medication but no adverse effects
  - Patient fell but no injuries sustained
  - Incorrect test performed but caught before treatment

### 3. NME - Near Miss Event 🔵
- **Definition**: Deviation occurred but did not reach the patient
- **Criteria**:
  - ✅ Deviation from GAPS occurred
  - ❌ Deviation did NOT reach the patient
- **Examples**:
  - Wrong medication prepared but caught before administration
  - Lab specimen mislabeled but caught before results reported
  - Equipment malfunction detected before patient contact

### 4. NSE - No Safety Event ⚪
- **Definition**: No deviation from Generally Accepted Performance Standards
- **Criteria**:
  - ❌ No deviation from GAPS occurred
- **Examples**:
  - Normal procedural delays
  - Routine equipment checks showing normal function
  - Patient complaints not related to safety standards

---

## GAPS (Generally Accepted Performance Standards)

Standards that define expected clinical and operational practices:
- Clinical protocols and guidelines
- Medication administration procedures
- Patient identification protocols
- Equipment maintenance standards
- Infection control measures
- Documentation requirements
- Communication protocols

---

## Three-Step Classification Process

### Step 1: GAPS Deviation Check
**Question**: Did a deviation from Generally Accepted Performance Standards occur?

**Prompt**: Analyzes incident description to determine if GAPS were violated

**Output**:
- `True` → Proceed to Step 2
- `False` → Classify as **NSE**

### Step 2: Patient Reach Assessment
**Question**: Did the deviation reach the patient?

**Prompt**: Determines if the incident directly affected the patient

**Output**:
- `True` → Proceed to Step 3
- `False` → Classify as **NME**

### Step 3: Harm Level Evaluation
**Question**: Did the patient experience moderate/severe harm or death?

**Prompt**: Assesses actual harm to the patient

**Output**:
- `True` → Classify as **SSE**
- `False` → Classify as **PSE**

---

## Color Coding (Frontend)

```css
NSE → Gray   (bg-gray-100, text-gray-800)
NME → Blue   (bg-blue-100, text-blue-800)
PSE → Yellow (bg-yellow-100, text-yellow-800)
SSE → Red    (bg-red-100, text-red-800)
```

---

## API Response Format

```json
{
  "incident": "Patient fell in hallway while walking to bathroom",
  "department": "internal medicine",
  "gaps_deviation_check": "Yes",
  "gaps_rationale": "Fall indicates deviation from safety protocols",
  "reached_patient_check": "Yes",
  "reached_patient_rationale": "Patient directly experienced the fall",
  "harm_level_check": "No",
  "harm_level_rationale": "No injuries reported",
  "final_classification_code": "PSE",
  "final_rationale": "Precursor Safety Event - deviation reached the patient with no or minimal harm.",
  "status": "success",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## Classification Statistics

Example batch processing summary:

```json
{
  "summary": {
    "SSE": 5,  // 5 serious events
    "PSE": 12, // 12 precursor events  
    "NME": 28, // 28 near misses
    "NSE": 3   // 3 non-events
  },
  "total_incidents": 48,
  "successful": 48,
  "failed": 0
}
```

---

## Department Categories

The system tracks incidents across 5 medical departments:

1. **internal_medicine** - Internal Medicine
2. **surgery** - Surgery
3. **ob_gyn_nicu** - OB/GYN/NICU
4. **radiology_imaging** - Radiology/Imaging
5. **outpatient_er** - Outpatient/ER

---

## Key Implementation Files

### Backend (Python/FastAPI)
- `src/model/safety_event_classifier.py` - Core classification logic
- `src/model/prompt_utils.py` - LLM prompts for 3-step process
- `src/api/services/classification_service.py` - API service layer

### Frontend (React/Next.js)
- `src/frontend-react/src/app/page.jsx` - Home page with code reference
- `src/frontend-react/src/app/globals.css` - Color styling for codes
- `src/frontend-react/src/app/classify/page.jsx` - Classification interface

---

## Important Notes

1. **Classification is deterministic**: Same incident always produces same code
2. **Rationales are provided**: Each step includes AI-generated reasoning
3. **Department tracking**: All incidents tagged with department
4. **Three prompts**: Each step uses specialized LLM prompt
5. **Transparent process**: All intermediate results returned

---

## Testing Examples

### NSE Example
```
Description: "Routine vital signs check completed on time"
Result: NSE - No deviation from protocols
```

### NME Example
```
Description: "Wrong medication prepared but caught before administration"
Result: NME - Caught before reaching patient
```

### PSE Example
```
Description: "Patient received wrong medication but no adverse effects"
Result: PSE - Reached patient but no harm
```

### SSE Example
```
Description: "Surgical instrument left inside patient during procedure"
Result: SSE - Serious harm requiring additional surgery
```

---

**Version**: 1.0  
**Last Updated**: January 2025  
**System**: Safety Event Classification System (AC215_888)
