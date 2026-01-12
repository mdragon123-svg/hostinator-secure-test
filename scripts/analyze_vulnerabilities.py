import requests
import csv
import io

def fetch_and_analyze_vulnerabilities():
    """Fetch and analyze Semgrep vulnerability reports"""
    
    # URLs for the vulnerability reports
    code_findings_url = "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Semgrep_Code_Findings_2025_08_13-IqhKUA6mhkpdwC9E5SEpRR7WjQ83jz.csv"
    supply_chain_url = "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Semgrep_Supply_Chain_Findings_2025_08_13-2jwgWhs1m1AqIIUcMeSKX6YOlF5jd7.csv"
    
    print("🔍 Fetching Semgrep Code Findings...")
    try:
        response = requests.get(code_findings_url)
        response.raise_for_status()
        
        # Parse CSV data
        csv_data = csv.DictReader(io.StringIO(response.text))
        code_findings = list(csv_data)
        
        print(f"✅ Found {len(code_findings)} code findings")
        
        # Analyze code findings
        print("\n📊 Code Findings Analysis:")
        for finding in code_findings:
            print(f"- Rule: {finding.get('Rule Name', 'N/A')}")
            print(f"  Severity: {finding.get('Severity', 'N/A')}")
            print(f"  File: {finding.get('Line Of Code Url', 'N/A').split('/')[-1].split('#')[0] if finding.get('Line Of Code Url') else 'N/A'}")
            print(f"  Description: {finding.get('Rule Description', 'N/A')[:100]}...")
            print()
            
    except Exception as e:
        print(f"❌ Error fetching code findings: {e}")
        code_findings = []
    
    print("\n🔍 Fetching Semgrep Supply Chain Findings...")
    try:
        response = requests.get(supply_chain_url)
        response.raise_for_status()
        
        # Parse CSV data
        csv_data = csv.DictReader(io.StringIO(response.text))
        supply_chain_findings = list(csv_data)
        
        print(f"✅ Found {len(supply_chain_findings)} supply chain findings")
        
        # Analyze supply chain findings
        print("\n📊 Supply Chain Findings Analysis:")
        for finding in supply_chain_findings:
            print(f"- Dependency: {finding.get('Dependency', 'N/A')}")
            print(f"  Version: {finding.get('Version', 'N/A')}")
            print(f"  Severity: {finding.get('Severity', 'N/A')}")
            print(f"  CVE: {finding.get('Cve', 'N/A')}")
            print(f"  EPSS: {finding.get('Epss', 'N/A')}")
            print(f"  Description: {finding.get('Rule Description', 'N/A')}")
            print()
            
    except Exception as e:
        print(f"❌ Error fetching supply chain findings: {e}")
        supply_chain_findings = []
    
    return code_findings, supply_chain_findings

if __name__ == "__main__":
    code_findings, supply_chain_findings = fetch_and_analyze_vulnerabilities()
    
    print(f"\n📋 Summary:")
    print(f"- Code Findings: {len(code_findings)}")
    print(f"- Supply Chain Findings: {len(supply_chain_findings)}")
