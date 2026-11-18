from dataclasses import dataclass
@dataclass
class RiskResult: score: float; category: str; explanation: str
def assess_risk(susceptibility,rainfall_1d,rainfall_3d,rainfall_7d,thresholds=None,anomaly=None):
    t=thresholds or {'one_day':[25,50,100],'three_day':[50,100,200],'seven_day':[100,200,400]}
    def norm(x,b): return min(x/max(b[-1],1),1.0)
    rain=.45*norm(rainfall_1d,t['one_day'])+.35*norm(rainfall_3d,t['three_day'])+.2*norm(rainfall_7d,t['seven_day']); score=max(0,min(1,.6*float(susceptibility)+.4*rain))
    cat='LOW' if score<.25 else 'MODERATE' if score<.5 else 'HIGH' if score<.75 else 'VERY HIGH'; d=[]
    if susceptibility>=.6:d.append('high static susceptibility')
    if rainfall_1d>=t['one_day'][1]:d.append('elevated 1-day rainfall')
    if rainfall_3d>=t['three_day'][1]:d.append('elevated 3-day rainfall')
    if rainfall_7d>=t['seven_day'][1]:d.append('elevated 7-day rainfall')
    if anomaly is not None and anomaly>1: d.append('positive rainfall anomaly')
    return RiskResult(score,cat,', '.join(d) or 'low recent rainfall and/or susceptibility')
