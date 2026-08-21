"""SOC context renderers."""
from . import analyst, malware, siem, threat_report

RENDERERS = {
    "siem": siem.render,
    "threat_report": threat_report.render,
    "malware": malware.render,
    "analyst": analyst.render,
}
