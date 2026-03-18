from app.services.severity_service import predict_severity, predict_resource_demand, Severity

def test_ai_predictions():
    print("--- Testing AI Severity Prediction ---")
    # Low scenario
    sev_low = predict_severity(20, 5, 2, 50, 1)
    print(f"Low Scenario: Predicted {sev_low}")
    
    # Critical scenario
    sev_crit = predict_severity(42, 300, 120, 5000, 10)
    print(f"Critical Scenario: Predicted {sev_crit}")

    print("\n--- Testing AI Resource Demand Prediction ---")
    # High Severity demand
    resources = predict_resource_demand(Severity.HIGH, 2000, 75)
    print(f"High Severity Resources: {resources}")
    
    # Critical Severity demand
    resources_crit = predict_resource_demand(Severity.CRITICAL, 5000, 95)
    print(f"Critical Severity Resources: {resources_crit}")

if __name__ == "__main__":
    test_ai_predictions()
