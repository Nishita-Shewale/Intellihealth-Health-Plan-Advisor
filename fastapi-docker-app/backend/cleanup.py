import re
import numpy as np


def clean_value(value, expected_type=str):
    """
    Cleans and converts values:
    - If expected_type is float: cleans currency symbols, %, and converts to float
    - If expected_type is str: returns the value as-is without cleaning
    - Converts known null values like 'nan' to None
    - Logs skipped numeric cleaning if field is a string that looks like a number but expected_type != float
    """
    if isinstance(value, str):
        value = value.strip()
        if value.lower() in {"nan", "not applicable", "n/a", "-", ""}:
            return None

        if expected_type == float:
            cleaned_value = re.sub(r"[^0-9.]", "", value)
            if cleaned_value.replace(".", "", 1).isdigit():
                return float(cleaned_value)
            return None  # Couldn't convert cleanly

        # 🧪 Debug: detect numeric-looking string that we're skipping because it's not expected as float
        if re.search(r"\d", value):
            pass

        return value  # Leave string as-is

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