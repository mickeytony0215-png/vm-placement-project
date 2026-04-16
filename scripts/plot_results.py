import json
import matplotlib.pyplot as plt
import pandas as pd
import glob
import os
from pathlib import Path

def plot_latest_results():
    # 1. 找到最新的結果 JSON 檔
    list_of_files = glob.glob('results/*.json') 
    if not list_of_files:
        print("❌ 在 results/ 資料夾中找不到 JSON 檔案！")
        print("   請先執行: python src/main.py --run-all")
        return
    
    # 找最新的那個檔案
    latest_file = max(list_of_files, key=os.path.getctime)
    print(f"📊 正在讀取數據: {latest_file}")

    # 2. 讀取數據
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 讀取檔案失敗: {e}")
        return

    # 確保數據是列表格式
    if not isinstance(data, list):
        print("⚠️ 警告: JSON 數據格式不是列表，可能無法正確繪圖。")
        # 嘗試將單一字典轉為列表
        data = [data]

    df = pd.DataFrame(data)

    # 確保有必要的欄位
    required_cols = ['algorithm', 'scale', 'active_pms', 'total_energy']
    if not all(col in df.columns for col in required_cols):
        print(f"❌ 數據缺少必要欄位，現有欄位: {df.columns.tolist()}")
        return

    # 確保 plots 資料夾存在
    output_dir = Path("results/plots")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 3. 畫圖：針對不同規模 (Small/Medium) 分別畫圖
    scales = df['scale'].unique()
    
    for scale in scales:
        plt.figure(figsize=(10, 6))
        
        # 篩選該規模的數據
        scale_df = df[df['scale'] == scale]
        
        if scale_df.empty:
            continue
            
        # 設定顏色 (FFD: 藍, BFD: 綠, NLP: 紅, RLS: 黃)
        colors = {'ffd': '#3498db', 'bfd': '#2ecc71', 'nlp': '#e74c3c', 'rls-ffd': '#f1c40f'}
        bar_colors = [colors.get(algo.lower(), '#95a5a6') for algo in scale_df['algorithm']]

        # 繪製長條圖 (Active PMs)
        bars = plt.bar(scale_df['algorithm'], scale_df['active_pms'], color=bar_colors)
        
        plt.title(f'Active PMs Comparison ({scale.capitalize()} Scale)', fontsize=14)
        plt.xlabel('Algorithm', fontsize=12)
        plt.ylabel('Number of Active PMs', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.3)
        
        # 在柱狀圖上方標示數值
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                     f'{int(height)}',
                     ha='center', va='bottom', fontweight='bold')

        # 存檔
        timestamp = Path(latest_file).stem.replace('results_', '')
        output_path = output_dir / f"active_pms_{scale}_{timestamp}.png"
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ 圖表已儲存: {output_path}")
        plt.close() # 關閉圖表釋放記憶體

if __name__ == "__main__":
    plot_latest_results()