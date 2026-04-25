"""
Run this script to generate sample charts for testing the app.
Usage: python generate_sample_charts.py
Creates a 'sample_charts/' folder with 5 ready-to-use test images.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

os.makedirs("sample_charts", exist_ok=True)


# 1. Line chart — revenue over time
fig, ax = plt.subplots(figsize=(9, 5))
quarters = ["Q1 '22", "Q2 '22", "Q3 '22", "Q4 '22",
            "Q1 '23", "Q2 '23", "Q3 '23", "Q4 '23",
            "Q1 '24", "Q2 '24"]
revenue  = [42, 47, 51, 63, 58, 65, 70, 89, 84, 97]
ax.plot(quarters, revenue, marker="o", linewidth=2.5, color="#6c63ff", markersize=7)
ax.fill_between(range(len(quarters)), revenue, alpha=0.1, color="#6c63ff")
ax.set_title("Quarterly Revenue ($ millions)", fontsize=14, fontweight="bold", pad=12)
ax.set_ylabel("Revenue ($M)")
ax.set_xlabel("Quarter")
ax.grid(axis="y", alpha=0.3)
ax.tick_params(axis="x", rotation=30)
plt.tight_layout()
plt.savefig("sample_charts/line_revenue.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ line_revenue.png")


# 2. Bar chart — regional sales comparison
fig, ax = plt.subplots(figsize=(9, 5))
regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
sales_2023 = [320, 210, 275, 85, 60]
sales_2024 = [380, 245, 340, 110, 78]
x = np.arange(len(regions))
w = 0.35
ax.bar(x - w/2, sales_2023, w, label="2023", color="#6c63ff", alpha=0.85)
ax.bar(x + w/2, sales_2024, w, label="2024", color="#ff6584", alpha=0.85)
ax.set_title("Regional Sales Comparison 2023 vs 2024 ($M)", fontsize=14, fontweight="bold", pad=12)
ax.set_xticks(x)
ax.set_xticklabels(regions, rotation=15, ha="right")
ax.set_ylabel("Sales ($M)")
ax.legend()
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("sample_charts/bar_regional_sales.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ bar_regional_sales.png")


# 3. Scatter plot — marketing spend vs conversion rate
fig, ax = plt.subplots(figsize=(8, 6))
np.random.seed(42)
spend = np.random.uniform(5, 100, 60)
conversion = 0.3 * spend + np.random.normal(0, 8, 60)
conversion = np.clip(conversion, 2, 45)
scatter = ax.scatter(spend, conversion, c=conversion, cmap="viridis",
                     s=80, alpha=0.75, edgecolors="white", linewidth=0.5)
m, b = np.polyfit(spend, conversion, 1)
x_line = np.linspace(5, 100, 100)
ax.plot(x_line, m * x_line + b, "r--", linewidth=1.5, alpha=0.7, label="Trend line")
plt.colorbar(scatter, label="Conversion rate (%)")
ax.set_title("Marketing Spend vs Conversion Rate", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Marketing Spend ($K)")
ax.set_ylabel("Conversion Rate (%)")
ax.legend()
ax.grid(alpha=0.2)
plt.tight_layout()
plt.savefig("sample_charts/scatter_marketing.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ scatter_marketing.png")


# 4. Heatmap — customer satisfaction by product & region
fig, ax = plt.subplots(figsize=(9, 5))
products = ["Product A", "Product B", "Product C", "Product D", "Product E"]
regions_h = ["NA", "EU", "APAC", "LATAM"]
data = np.array([
    [4.2, 3.8, 4.5, 3.1],
    [3.9, 4.1, 3.7, 4.0],
    [4.6, 4.4, 4.8, 3.5],
    [3.2, 3.6, 4.0, 2.9],
    [4.4, 4.7, 4.3, 4.1],
])
im = ax.imshow(data, cmap="RdYlGn", vmin=2.5, vmax=5.0, aspect="auto")
plt.colorbar(im, ax=ax, label="Satisfaction Score (1–5)")
ax.set_xticks(range(len(regions_h)))
ax.set_xticklabels(regions_h)
ax.set_yticks(range(len(products)))
ax.set_yticklabels(products)
for i in range(len(products)):
    for j in range(len(regions_h)):
        ax.text(j, i, f"{data[i,j]:.1f}", ha="center", va="center",
                fontsize=11, fontweight="bold",
                color="white" if data[i,j] < 3.3 else "black")
ax.set_title("Customer Satisfaction Heatmap by Product & Region", fontsize=13, fontweight="bold", pad=12)
plt.tight_layout()
plt.savefig("sample_charts/heatmap_satisfaction.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ heatmap_satisfaction.png")


# 5. Pie chart — market share
fig, ax = plt.subplots(figsize=(8, 6))
labels = ["Company A", "Company B", "Company C", "Company D", "Others"]
sizes  = [34, 27, 18, 12, 9]
colors = ["#6c63ff", "#ff6584", "#43b89c", "#ffa94d", "#adb5bd"]
explode = (0.05, 0, 0, 0, 0)
wedges, texts, autotexts = ax.pie(
    sizes, labels=labels, colors=colors, explode=explode,
    autopct="%1.1f%%", startangle=140,
    textprops={"fontsize": 11},
    wedgeprops={"edgecolor": "white", "linewidth": 2}
)
for at in autotexts:
    at.set_fontweight("bold")
ax.set_title("Global Market Share — Cloud Storage (2024)", fontsize=13, fontweight="bold", pad=15)
plt.tight_layout()
plt.savefig("sample_charts/pie_market_share.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ pie_market_share.png")

print("\n✅ All sample charts saved to sample_charts/")
print("   Upload any of these to the app to test it!")
