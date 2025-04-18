import os
from neo4j_utils import neo4j_driver 
from collections import defaultdict

def clean_value(value):
    if isinstance(value, str):  # Only clean strings
        value = value.replace("$", "").replace(",", "").replace("%", "")  # Remove $, , and %
    try:
        return float(value)  # Convert to float if possible
    except ValueError:
        return None  # Return None for invalid values
    
def apply_dynamic_rule(driver, rule_name, patient_filter, attribute_list):
    """
    Applies a dynamic rule for filtering insurance plans in Neo4j, ensuring balanced filtering across plan types.

    Parameters:
    - driver: Neo4j driver instance.
    - rule_name: Name of the rule (e.g., "Diabetes", "Maternity").
    - patient_filter: Condition to match patients (e.g., age > 50, has diabetes).
    - attribute_list: List of plan attributes to filter on (e.g., deductible, coinsurance).
    """

    with driver.session() as session:
        # Step 1: Get distinct plan types
        plan_types_query = "MATCH (plan:Plan) RETURN DISTINCT plan.PlanType AS plan_type"
        plan_types_result = session.run(plan_types_query)
        plan_types = [record["plan_type"] for record in plan_types_result if record["plan_type"]]

        if not plan_types:
            print("⚠ No plan types found. Skipping rule.")
            return None

        # Step 2: Process each plan type independently
        all_results = {"patient": None, "plans": []}
        for plan_type in plan_types:
            # Build dynamic query for stats
            attribute_conditions = " AND ".join(
                [f"plan.{attr} IS NOT NULL" for attr in attribute_list]
            )
            stats_query = f"""
            MATCH (plan:Plan)
            WHERE plan.PlanType = '{plan_type}'
            AND {attribute_conditions}
            RETURN 
                {", ".join([f"percentileCont(toFloat(plan.{attr}), 0.5) AS median_{attr}" for attr in attribute_list])}
            """

            stats_result = session.run(stats_query).single()
            if not stats_result:
                print(f"⚠ No valid stats found for plan type {plan_type} in {rule_name}. Skipping this type.")
                continue

            # Extract computed statistics
            medians = {attr: stats_result[f"median_{attr}"] for attr in attribute_list if stats_result[f"median_{attr}"] is not None}
            print(f"Computed medians for {plan_type}: {medians}")
            if not medians:
                print(f"⚠ No median values computed for plan type {plan_type} in {rule_name}. Skipping this type.")
                continue

            filter_conditions = " AND ".join(
                [f"toFloat(plan.{attr}) <= ${attr}" for attr in medians]
            )
            print(f"Filter conditions for {plan_type}: {filter_conditions}")
            query = f"""
            MATCH (p:Patient), (plan:Plan)
            WHERE plan.PlanType = '{plan_type}'
            AND {patient_filter}
            AND {filter_conditions}
            MERGE (p)-[:{rule_name.replace(" ", "_").upper()}]->(plan)
            RETURN p AS patient, plan
            """

            # Run query for this plan type
            result = session.run(query, **medians)

            # Collect results
            for record in result:
                if all_results["patient"] is None:
                    all_results["patient"] = {key: record["patient"][key] for key in record["patient"].keys()}
                all_results["plans"].append({key: record["plan"][key] for key in record["plan"].keys()})

        return all_results if all_results["plans"] else None


def apply_selected_rules(driver, patient):
    """
    Applies Neo4j filtering rules dynamically based on patient demographics.
    
    Parameters:
    - driver: Neo4j driver instance.
    - patient: Patient dictionary containing demographic details.
    
    Returns:
    - Dictionary containing applied rules and their matched plans.
    """
    selected_rules = []

    # Rule 1: Diabetes-Specific Plans
    if "Diabetes" in patient["medical_conditions"]:
        selected_rules.append({
            "rule_name": "Diabetes",
            "patient_filter": f"p.id = {patient['id']}",
            "attribute_list": [
                "SBCHavingDiabetesCoinsurance",
                "SBCHavingDiabetesDeductible",
                "SBCHavingDiabetesLimit",
                "SBCHavingDiabetesCopayment"
            ]
        })

    # Rule 2: Maternity Plans
    if patient["gender"].lower() == "female" and 18 <= patient["age"] <= 45:
        selected_rules.append({
            "rule_name": "Maternity",
            "patient_filter": f"p.id = {patient['id']}",
            "attribute_list": [
                "SBCHavingaBabyDeductible",
                "SBCHavingaBabyCoinsurance",
                "SBCHavingaBabyLimit",
                "SBCHavingaBabyCopayment"
            ]
        })

    # Rule 3: Older Adults
    if patient["age"] >= 50:
        selected_rules.append({
            "rule_name": "Older_Adults",
            "patient_filter": f"p.id = {patient['id']}",
            "attribute_list": [
                "TEHBInnTier1IndividualMOOP",
                "TEHBDedInnTier1Individual",
                "TEHBDedInnTier1Coinsurance"
            ]
        })

    # Rule 4: Family Coverage
    if patient["family_coverage"]:
        selected_rules.append({
            "rule_name": "Family_Coverage",
            "patient_filter": f"p.id = {patient['id']}",
            "attribute_list": [
                "TEHBDedInnTier1FamilyPerPerson",
                "TEHBDedOutOfNetFamilyPerPerson",
                "TEHBInnTier1FamilyPerPersonMOOP",
                "TEHBDedInnTier1FamilyPerGroup",
                "TEHBInnTier1FamilyPerGroupMOOP"
            ]
        })

    # Rule 5: Default (General Filtering)
    if not selected_rules:
        selected_rules.append({
            "rule_name": "Default",
            "patient_filter": f"p.id = {patient['id']}",
            "attribute_list": [
                "TEHBDedInnTier1Individual",
                "TEHBDedInnTier1Coinsurance",
                "TEHBInnTier1IndividualMOOP"
            ]
        })

    print(f"Selected rules: {selected_rules}")
    results = {}
    for rule in selected_rules:
        rule_result = apply_dynamic_rule(driver, **rule)
        if rule_result:
            results[rule["rule_name"]] = rule_result

    return results if results else None

def get_plan_distribution(driver, patient_id):
    """
    Get the distribution of how many rules are satisfied by each plan for a given patient.
    For each rule count, also return summary of which rule combinations exist.
    """
    with driver.session() as session:
        query = """
        MATCH (p:Patient)-[r]->(plan:Plan)
        WHERE p.id = $patient_id
        RETURN plan.PlanId AS plan_id, 
               plan.PlanType AS plan_type, 
               type(r) AS rule_name
        """

        result = session.run(query, patient_id=patient_id)

        # Step 1: Collect rule names per plan
        plan_details = {}
        for record in result:
            try:
                plan_id = record["plan_id"]
                plan_type = record.get("plan_type", "Unknown")
                rule_name = record["rule_name"]
                if plan_id not in plan_details:
                    plan_details[plan_id] = {
                        "plan_type": plan_type,
                        "rule_names": set()
                    }
                if rule_name != "CONSIDERS":
                    plan_details[plan_id]["rule_names"].add(rule_name)

            except KeyError as e:
                print(f"⚠️ Skipping record due to missing field: {e}")

        if not plan_details:
            return {}, {}, 0

        # Step 2: Group plans by rule count and rule set
        rule_count_to_rule_sets = defaultdict(list)
        for details in plan_details.values():
            rules = tuple(sorted(details["rule_names"]))
            rule_count = len(rules)
            rule_count_to_rule_sets[rule_count].append(rules)

        # Step 3: Aggregate into summarized format
        plan_distribution = {}
        for rule_count, rule_sets in rule_count_to_rule_sets.items():
            summary = defaultdict(int)
            for rule_set in rule_sets:
                summary[rule_set] += 1

            plan_distribution[rule_count] = {
                "count": len(rule_sets),  # total plans with this rule count
                "rule_sets_summary": [
                    {
                        "rules": list(rule_set),
                        "count": count
                    } for rule_set, count in summary.items()
                ]
            }

        # Step 4: Find highest rule count
        highest_rule_count = max(plan_distribution.keys())

        # Step 5: Compute plan type distribution for highest rule count
        plan_type_distribution = {}
        for plan_id, details in plan_details.items():
            if len(details["rule_names"]) == highest_rule_count:
                plan_type = details["plan_type"]
                plan_type_distribution[plan_type] = plan_type_distribution.get(plan_type, 0) + 1

        return plan_distribution, plan_type_distribution, highest_rule_count


def get_plans_by_type_from_neo4j(driver, patient_id, plan_type, highest_rule_count):
    """
    Queries Neo4j to get all plans of the specified plan type for the given patient, but only those plans
    that satisfy the highest number of rules.
    """
    with driver.session() as session:
        # Fetch plans of the selected plan type for the given patient and rule count
        query = """
            MATCH (p:Patient)-[r]->(plan:Plan)
            WHERE p.id = $patient_id
            AND plan.PlanType = $plan_type
            WITH plan, COUNT(r) AS rule_count
            WHERE rule_count = $highest_rule_count
            RETURN plan
            """
        
        result = session.run(query, patient_id=patient_id, plan_type=plan_type, highest_rule_count=highest_rule_count)
        
        # Collect the plans from the result
        plans = [record["plan"] for record in result]
        
        return plans


def get_plan_ids_from_neo4j(driver, patient_id, plan_type, highest_rule_count):
    """
    Queries Neo4j to get the list of PlanIds that match the highest rule count for the given patient and plan type.
    """
    with driver.session() as session:
        query = """
            MATCH (p:Patient)-[r]->(plan:Plan)
            WHERE p.id = $patient_id
            AND plan.PlanType = $plan_type
            WITH plan.PlanId AS PlanId, COUNT(r) AS rule_count
            WHERE rule_count = $highest_rule_count
            RETURN PlanId
            """
        
        result = session.run(query, patient_id=patient_id, plan_type=plan_type, highest_rule_count=highest_rule_count)
        
        # Extract only PlanIds
        plan_ids = [record["PlanId"] for record in result]
        
        return plan_ids
