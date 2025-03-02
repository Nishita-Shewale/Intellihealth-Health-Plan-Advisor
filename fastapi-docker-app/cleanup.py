import re
import numpy as np

def clean_value(value,expected_type=str):
    """
    Cleans and converts values:
    - Converts numeric attributes to floats
    - Converts 'NaN', 'nan', 'NAN', etc. to None
    - Strips unwanted characters (e.g., '$', 'per person', 'per group') from numeric values
    """
    if isinstance(value, str):
        value = value.strip()  # Remove extra spaces
        value_lower = value.lower()

        # Convert all cases of "NaN" or "Not Applicable" to None
        if value_lower in {"nan", "not applicable", "n/a", "-"}:
            return None

        # Remove dollar signs, commas, and extra text (e.g., "$500 per person" → "500")
        cleaned_value = re.sub(r"[^0-9.]", "", value)

        # Convert to float if it's a number and belongs to numeric attributes
        if cleaned_value.replace(".", "", 1).isdigit():
            return float(cleaned_value)

    # Convert numpy NaN to None
    if isinstance(value, float) and np.isnan(value):
        return None

    return value 
    
ATTRIBUTE_CLEANUP_CONFIG = {
    # Diabetes-related attributes
    "SBCHavingDiabetesCoinsurance": float,
    "SBCHavingDiabetesDeductible": float,
    "SBCHavingDiabetesLimit": float,
    "SBCHavingDiabetesCopayment": float,

    # Maternity-related attributes
    "SBCHavingaBabyDeductible": float,
    "SBCHavingaBabyCoinsurance": float,
    "SBCHavingaBabyLimit": float,
    "SBCHavingaBabyCopayment": float,

    # Older adults attributes
    "TEHBInnTier1IndividualMOOP": float,
    "TEHBDedInnTier1Individual": float,
    "TEHBDedInnTier1Coinsurance": float,

    # Family-related attributes
    "TEHBDedInnTier1FamilyPerPerson": float,
    "TEHBDedOutOfNetFamilyPerPerson": float,
    "TEHBInnTier1FamilyPerPersonMOOP": float,
    "TEHBDedInnTier1FamilyPerGroup": float,
    "TEHBInnTier1FamilyPerGroupMOOP": float,

    # Default stats-related attributes
    "TEHBDedInnTier1Individual": float,
    "TEHBDedInnTier1Coinsurance": float,
    "TEHBInnTier1IndividualMOOP": float,
}