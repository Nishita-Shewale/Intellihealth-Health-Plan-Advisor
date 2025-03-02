# schemas.py
from pydantic import BaseModel, Field
from typing import Optional, Any, List
from enum import Enum
import pandas as pd

df = pd.read_csv("cleaned_plans_data.csv")  # Replace with your cleaned file path

# Enums for controlled values
class PhysicalActivityLevel(str, Enum):
    sedentary = "sedentary"
    moderate = "moderate"
    active = "active"

class BudgetCategory(str, Enum):
    bronze = "Bronze"
    silver = "Silver"
    gold = "Gold"
    platinum = "Platinum"

# Base Schema
class PatientBase(BaseModel):
    name: str
    age: int
    gender: str
    state: str
    occupation: Optional[str] = None
    smoking_status: bool = False  # Boolean field defaulting to False
    physical_activity_level: PhysicalActivityLevel
    medical_conditions: Optional[List[str]] = []  # List of medical conditions
    travel_coverage_needed: bool = False  # Boolean field defaulting to False
    family_coverage: bool = False  # Boolean field defaulting to False
    budget_category: Optional[BudgetCategory] = None  # Enum for budget categories
    has_offspring: bool  # New Field
    is_married: bool

# Schema for creating patients
class PatientCreate(PatientBase):
    pass

# Schema for reading patients
class Patient(PatientBase):
    id: int

    class Config:
        from_attributes = True

class InsurancePlan(BaseModel):
    id: int
    BusinessYear: int
    StateCode: str
    IssuerId: int
    IssuerMarketPlaceMarketingName: Optional[str]
    MarketCoverage: Optional[str]
    DentalOnlyPlan: Optional[str]
    PlanMarketingName: Optional[str]
    PlanType: Optional[str]
    MetalLevel: Optional[str]
    IsNoticeRequiredForPregnancy: Optional[str]
    IsReferralRequiredForSpecialist: Optional[str]
    SpecialistRequiringReferral: Optional[str]
    PlanLevelExclusions: Optional[str]
    ChildOnlyOffering: Optional[str]
    WellnessProgramOffered: Optional[str]
    DiseaseManagementProgramsOffered: Optional[str]
    EHBPercentTotalPremium: Optional[float]
    PlanEffectiveDate: Optional[str]
    PlanExpirationDate: Optional[str]
    OutOfCountryCoverage: Optional[str]
    OutOfCountryCoverageDescription: Optional[str]
    OutOfServiceAreaCoverage: Optional[str]
    OutOfServiceAreaCoverageDescription: Optional[str]
    NationalNetwork: Optional[str]
    PlanId: Optional[str]
    IssuerActuarialValue: Optional[str]
    MedicalDrugDeductiblesIntegrated: Optional[str]
    MedicalDrugMaximumOutofPocketIntegrated: Optional[str]
    MultipleInNetworkTiers: Optional[str]
    SBCHavingaBabyDeductible: Optional[str]
    SBCHavingaBabyCopayment: Optional[str]
    SBCHavingaBabyCoinsurance: Optional[str]
    SBCHavingaBabyLimit: Optional[str]
    SBCHavingDiabetesDeductible: Optional[str]
    SBCHavingDiabetesCopayment: Optional[str]
    SBCHavingDiabetesCoinsurance: Optional[str]
    SBCHavingDiabetesLimit: Optional[str]
    SBCHavingSimplefractureDeductible: Optional[str]
    SBCHavingSimplefractureCopayment: Optional[str]
    SBCHavingSimplefractureCoinsurance: Optional[str]
    SBCHavingSimplefractureLimit: Optional[str]
    SpecialtyDrugMaximumCoinsurance: Optional[str]
    InpatientCopaymentMaximumDays: Optional[int]
    BeginPrimaryCareCostSharingAfterNumberOfVisits: Optional[int]
    BeginPrimaryCareDeductibleCoinsuranceAfterNumberOfCopays: Optional[int]
    MEHBInnTier1IndividualMOOP: Optional[str]
    MEHBInnTier1FamilyPerPersonMOOP: Optional[str]
    MEHBInnTier1FamilyPerGroupMOOP: Optional[str]
    MEHBInnTier2IndividualMOOP: Optional[str]
    MEHBInnTier2FamilyPerPersonMOOP: Optional[str]
    MEHBInnTier2FamilyPerGroupMOOP: Optional[str]
    DEHBInnTier1IndividualMOOP: Optional[str]
    DEHBInnTier1FamilyPerPersonMOOP: Optional[str]
    DEHBInnTier1FamilyPerGroupMOOP: Optional[str]
    DEHBInnTier2IndividualMOOP: Optional[float]
    DEHBInnTier2FamilyPerPersonMOOP: Optional[float]
    DEHBInnTier2FamilyPerGroupMOOP: Optional[float]
    TEHBInnTier1IndividualMOOP: Optional[str]
    TEHBInnTier1FamilyPerPersonMOOP: Optional[str]
    TEHBInnTier1FamilyPerGroupMOOP: Optional[str]
    TEHBInnTier2IndividualMOOP: Optional[str]
    TEHBInnTier2FamilyPerPersonMOOP: Optional[str]
    TEHBInnTier2FamilyPerGroupMOOP: Optional[str]
    MEHBDedInnTier1Individual: Optional[str]
    MEHBDedInnTier1FamilyPerPerson: Optional[str]
    MEHBDedInnTier1FamilyPerGroup: Optional[str]
    MEHBDedInnTier1Coinsurance: Optional[str]
    MEHBDedInnTier2Individual: Optional[str]
    MEHBDedInnTier2FamilyPerPerson: Optional[str]
    MEHBDedInnTier2FamilyPerGroup: Optional[str]
    MEHBDedInnTier2Coinsurance: Optional[str]
    MEHBDedOutOfNetIndividual: Optional[str]
    MEHBDedOutOfNetFamilyPerPerson: Optional[str]
    MEHBDedOutOfNetFamilyPerGroup: Optional[str]
    MEHBDedCombInnOonIndividual: Optional[str]
    MEHBDedCombInnOonFamilyPerPerson: Optional[str]
    MEHBDedCombInnOonFamilyPerGroup: Optional[str]
    DEHBDedInnTier1Individual: Optional[str]
    DEHBDedInnTier1FamilyPerPerson: Optional[str]
    DEHBDedInnTier1FamilyPerGroup: Optional[str]
    DEHBDedInnTier1Coinsurance: Optional[str]
    DEHBDedInnTier2Individual: Optional[str]
    DEHBDedInnTier2FamilyPerPerson: Optional[str]
    DEHBDedInnTier2FamilyPerGroup: Optional[str]
    DEHBDedInnTier2Coinsurance: Optional[str]
    DEHBDedOutOfNetIndividual: Optional[str]
    DEHBDedOutOfNetFamilyPerPerson: Optional[str]
    DEHBDedOutOfNetFamilyPerGroup: Optional[str]
    DEHBDedCombInnOonIndividual: Optional[str]
    DEHBDedCombInnOonFamilyPerPerson: Optional[str]
    DEHBDedCombInnOonFamilyPerGroup: Optional[str]
    TEHBDedInnTier1Individual: Optional[str]
    TEHBDedInnTier1FamilyPerPerson: Optional[str]
    TEHBDedInnTier1FamilyPerGroup: Optional[str]
    TEHBDedInnTier1Coinsurance: Optional[str]
    TEHBDedInnTier2Individual: Optional[str]
    TEHBDedInnTier2FamilyPerPerson: Optional[str]
    TEHBDedInnTier2FamilyPerGroup: Optional[str]
    TEHBDedInnTier2Coinsurance: Optional[str]
    TEHBDedOutOfNetIndividual: Optional[str]
    TEHBDedOutOfNetFamilyPerPerson: Optional[str]
    TEHBDedOutOfNetFamilyPerGroup: Optional[str]
    TEHBDedCombInnOonIndividual: Optional[str]
    TEHBDedCombInnOonFamilyPerPerson: Optional[str]
    TEHBDedCombInnOonFamilyPerGroup: Optional[str]
    IsHSAEligible: Optional[str]
    HSAOrHRAEmployerContribution: Optional[str]
    HSAOrHRAEmployerContributionAmount: Optional[str]

    class Config:
        from_attributes = True

class PatientID(BaseModel):
    patient_id: int