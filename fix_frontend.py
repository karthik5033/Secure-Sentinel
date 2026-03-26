import os
import re

base_dir = r'd:\coding_files\Projects\DTLshit\my-app'

replacements = {
    'components/ExplanationPanel.tsx': (r'prob > 0\.7', r'prob > 0.75'),
    'components/RiskMeter.tsx': (r'score > 0\.7 \?', r'score > 0.75 ?'),
    'app/test/page.tsx': (r'score > 0\.7', r'score > 0.75'),
    'app/features/neural-detection/page.tsx': (r'> 0\.7 \?', r'> 0.75 ?'),
    'app/features/temporal-analysis/page.tsx': [
        (r'riskScore > 0\.7', r'riskScore > 0.75'),
        (r'Risk &gt; 0\.7', r'Risk &gt; 0.75'),
        (r'score > 0\.7', r'score > 0.75')
    ],
    'app/how-it-works/page.tsx': (r'Score > 0\.7', r'Score > 0.75'),
    'app/features/quantum-defense/feature.service.ts': (r'risk_score > 0\.7', r'risk_score > 0.75'),
    'app/features/behavioral-baseline/page.tsx': (r'score > 0\.7', r'score > 0.75'),
    'app/dashboard/activity/page.tsx': (r'risk_score > 0\.7 \?', r'risk_score > 0.75 ?')
}

for rel_path, reps in replacements.items():
    full_path = os.path.join(base_dir, rel_path.replace('/', os.sep))
    if not os.path.exists(full_path):
        continue
        
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if isinstance(reps, tuple):
        reps = [reps]
        
    for before, after in reps:
        content = re.sub(before, after, content)
        
    # Also manual replace in RiskMeter.tsx since regex might miss some
    if "RiskMeter.tsx" in full_path:
        content = content.replace("s > 0.7", "s > 0.75")
        
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Done fixing frontend 0.7 occurrences.")
