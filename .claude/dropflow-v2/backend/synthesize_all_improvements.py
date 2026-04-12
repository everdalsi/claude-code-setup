#!/usr/bin/env python3
"""Synthesize all improvement analyses into unified recommendations"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

MEDIA_DIR = Path.home() / 'dropflow-media'

def synthesize_reports():
    """Aggregate all analysis reports and identify top improvements"""

    # Load all ANALYSIS_REPORT_*.json files
    analysis_files = sorted(MEDIA_DIR.glob('ANALYSIS_REPORT_*.json'))
    print(f"[LOAD] Found {len(analysis_files)} analysis reports")

    all_technologies = defaultdict(int)
    all_insights = defaultdict(int)
    all_domains = defaultdict(int)

    for report_file in analysis_files:
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract technologies
            if 'analysis' in data and 'all_technologies' in data['analysis']:
                for tech in data['analysis']['all_technologies']:
                    all_technologies[tech] += 1

            # Extract insights
            if 'analysis' in data and 'all_insights' in data['analysis']:
                for insight in data['analysis']['all_insights']:
                    all_insights[insight] += 1

            # Extract domain
            if 'analysis' in data and 'domain' in data['analysis']:
                domain = data['analysis']['domain']
                all_domains[domain] += 1

        except Exception as e:
            print(f"[ERROR] {report_file.name}: {e}")
            continue

    # Sort by frequency
    top_technologies = sorted(all_technologies.items(), key=lambda x: x[1], reverse=True)[:15]
    top_insights = sorted(all_insights.items(), key=lambda x: x[1], reverse=True)[:15]

    # Also load SELF_IMPROVEMENT reports for synthesis priorities
    self_improvement_files = sorted(MEDIA_DIR.glob('SELF_IMPROVEMENT_*.json'))
    print(f"[LOAD] Found {len(self_improvement_files)} self-improvement reports")

    synthesized_priorities = []
    for report_file in self_improvement_files:
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'improvement_synthesis' in data:
                    synthesis = data['improvement_synthesis']
                    synthesized_priorities.append({
                        'file': report_file.name,
                        'top_3': synthesis.get('top_3_priorities', []),
                        'tools': synthesis.get('tools_to_integrate', []),
                        'capabilities': synthesis.get('new_capabilities', [])
                    })
        except:
            pass

    # Aggregate priorities across all syntheses
    priority_counts = defaultdict(int)
    tool_counts = defaultdict(int)
    capability_counts = defaultdict(int)

    for synthesis in synthesized_priorities:
        for priority in synthesis['top_3']:
            priority_counts[priority['improvement']] += 1
        for tool in synthesis['tools']:
            tool_counts[tool] += 1
        for cap in synthesis['capabilities']:
            capability_counts[cap] += 1

    # Build final synthesis
    final_synthesis = {
        'timestamp': datetime.now().isoformat(),
        'reports_analyzed': len(analysis_files),
        'self_improvement_reports': len(self_improvement_files),
        'top_technologies_identified': [{'tech': t, 'frequency': f} for t, f in top_technologies],
        'top_insights_repeated': [{'insight': i, 'frequency': f} for i, f in top_insights],
        'domains': [{'domain': d, 'count': c} for d, c in sorted(all_domains.items(), key=lambda x: x[1], reverse=True)],
        'priority_improvements': sorted(priority_counts.items(), key=lambda x: x[1], reverse=True),
        'tools_to_integrate': sorted(tool_counts.items(), key=lambda x: x[1], reverse=True),
        'capabilities_to_add': sorted(capability_counts.items(), key=lambda x: x[1], reverse=True)
    }

    # Save synthesis
    synthesis_path = MEDIA_DIR / f'SYNTHESIS_{int(datetime.now().timestamp())}.json'
    with open(synthesis_path, 'w', encoding='utf-8') as f:
        json.dump(final_synthesis, f, ensure_ascii=False, indent=2)

    return final_synthesis

def main():
    print("="*70)
    print("[SYNTHESIS] Aggregating all improvement analyses")
    print("="*70)

    synthesis = synthesize_reports()

    print(f"\n[REPORTS ANALYZED] {synthesis['reports_analyzed']} analysis + {synthesis['self_improvement_reports']} self-improvement")

    print(f"\n[TOP TECHNOLOGIES]")
    for item in synthesis['top_technologies_identified'][:10]:
        print(f"  {item['tech']}: {item['frequency']}x")

    print(f"\n[TOP INSIGHTS]")
    for item in synthesis['top_insights_repeated'][:8]:
        print(f"  {item['insight']}: {item['frequency']}x")

    print(f"\n[TOP PRIORITY IMPROVEMENTS]")
    for improvement, count in synthesis['priority_improvements'][:5]:
        print(f"  [{count}x] {improvement}")

    print(f"\n[TOP TOOLS TO INTEGRATE]")
    for tool, count in synthesis['tools_to_integrate'][:10]:
        print(f"  [{count}x] {tool}")

    print(f"\n[NEW CAPABILITIES]")
    for cap, count in synthesis['capabilities_to_add'][:8]:
        print(f"  [{count}x] {cap}")

if __name__ == '__main__':
    main()
