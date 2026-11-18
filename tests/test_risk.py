from src.risk.risk_engine import assess_risk
def test_risk_categories():
    assert assess_risk(0,0,0,0).category=='LOW'
    assert assess_risk(1,500,800,1500).category=='VERY HIGH'
