import os
import yaml
from typing import Dict, Any, List, Tuple
from app.schemas.policy import PolicySimulationResponse, PolicyCheckResult, RuleCheckResult

class PolicyEngine:
    """
    Compiles YAML rules configs and executes comparison operators against transaction properties.
    """
    def __init__(self, yaml_path: str = "configs/policies.yaml") -> None:
        self.yaml_path = yaml_path
        self.policies = self._load_policies()

    def _load_policies(self) -> List[Dict[str, Any]]:
        """
        Helper resolving YAML inputs. Falls back to baseline definitions if file missing.
        """
        if os.path.exists(self.yaml_path):
            try:
                with open(self.yaml_path, "r") as f:
                    data = yaml.safe_load(f)
                    return data.get("policies", [])
            except Exception:
                pass
        
        # Hardcoded baseline defaults for testing/fallback integrity
        return [
            {
                "id": "POL-RBI-101",
                "type": "RBI",
                "name": "Foreign Outward Remittance Limit",
                "rules": [
                    {"field": "currency", "operator": "equals", "value": "USD"},
                    {"field": "amount", "operator": "less_than_or_equal", "value": 10000.00}
                ]
            },
            {
                "id": "POL-AML-202",
                "type": "AML",
                "name": "Structuring Protection",
                "rules": [
                    {"field": "amount", "operator": "not_between", "value": [4500.00, 4999.99]}
                ]
            },
            {
                "id": "POL-KYC-303",
                "type": "KYC",
                "name": "Active Account Enforcements",
                "rules": [
                    {"field": "account.status", "operator": "equals", "value": "active"}
                ]
            }
        ]

    def resolve_field(self, field_path: str, obj: Dict[str, Any]) -> Any:
        """
        Dynamically extracts nested dictionary values using dot-notation.
        E.g. resolve_field("account.customer.status", tx) -> tx["account"]["customer"]["status"]
        """
        parts = field_path.split(".")
        current = obj
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current

    def evaluate_rule(self, operator: str, expected: Any, actual: Any) -> bool:
        """
        Performs logic evaluation for dynamic rule operators.
        """
        if actual is None:
            return False

        try:
            if operator == "equals":
                return str(actual).strip() == str(expected).strip()
            elif operator == "not_equals":
                return str(actual).strip() != str(expected).strip()
            elif operator == "less_than":
                return float(actual) < float(expected)
            elif operator == "less_than_or_equal":
                return float(actual) <= float(expected)
            elif operator == "greater_than":
                return float(actual) > float(expected)
            elif operator == "greater_than_or_equal":
                return float(actual) >= float(expected)
            elif operator == "in":
                return actual in expected if isinstance(expected, list) else actual == expected
            elif operator == "not_in":
                return actual not in expected if isinstance(expected, list) else actual != expected
            elif operator == "between":
                return float(expected[0]) <= float(actual) <= float(expected[1])
            elif operator == "not_between":
                return not (float(expected[0]) <= float(actual) <= float(expected[1]))
        except Exception:
            return False
        return False

    def evaluate_transaction(self, transaction: Dict[str, Any]) -> PolicySimulationResponse:
        """
        Checks a proposed transaction payload against all loaded policies.
        """
        policies_checked: List[PolicyCheckResult] = []
        overall_pass = True

        for policy in self.policies:
            policy_id = policy.get("id", "UNKNOWN")
            name = policy.get("name", "Unnamed Policy")
            ptype = policy.get("type", "General")
            
            rules_checked: List[RuleCheckResult] = []
            policy_pass = True

            for rule in policy.get("rules", []):
                field = rule.get("field")
                operator = rule.get("operator")
                expected = rule.get("value")
                
                # Resolve transaction actual value
                actual = self.resolve_field(field, transaction)
                
                # Run operator check
                rule_pass = self.evaluate_rule(operator, expected, actual)
                
                if not rule_pass:
                    policy_pass = False
                    overall_pass = False

                rules_checked.append(RuleCheckResult(
                    field=field,
                    operator=operator,
                    expected=expected,
                    actual=actual,
                    status="pass" if rule_pass else "fail"
                ))

            policies_checked.append(PolicyCheckResult(
                policy_id=policy_id,
                name=name,
                type=ptype,
                status="pass" if policy_pass else "fail",
                rules_checked=rules_checked
            ))

        return PolicySimulationResponse(
            overall_status="pass" if overall_pass else "fail",
            policies_checked=policies_checked
        )
