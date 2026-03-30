import json
import matplotlib.pyplot as plt
import numpy as np

# Load data
try:
    with open('benchmark_results.json', 'r') as f:
        results = json.load(f)
except FileNotFoundError:
    print("Error: benchmark_results.json not found. Run benchmark_vrp.py first.")
    exit()

names = [r['name'] for r in results]
original = [r['original_dist'] for r in results]
optimized = [r['optimized_dist'] for r in results]
improvement = [r['improvement'] for r in results]

x = np.arange(len(names))
width = 0.35

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Plot 1: Distance Comparison
rects1 = ax1.bar(x - width/2, original, width, label='Quãng đường gốc (Naive)', color='lightgrey')
rects2 = ax1.bar(x + width/2, optimized, width, label='Quãng đường tối ưu (OR-Tools)', color='skyblue')

ax1.set_ylabel('Khoảng cách (km)')
ax1.set_title('So sánh Quãng đường (Trước và Sau tối ưu)')
ax1.set_xticks(x)
ax1.set_xticklabels(names)
ax1.legend()

# Plot 2: Improvement % (Gap Analysis)
ax2.bar(names, improvement, color='lightgreen')
ax2.set_ylabel('Tỷ lệ tiết kiệm (%)')
ax2.set_title('Hiệu quả giảm thiểu quãng đường (Saved %)')
for i, v in enumerate(improvement):
    ax2.text(i, v + 1, f"{v:.1f}%", ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('performance_metrics.png')
print("Visualization saved to performance_metrics.png")
plt.show() # Attempt to show if graphical env exists
