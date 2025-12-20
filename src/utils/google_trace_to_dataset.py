import os
import json
import random
from pathlib import Path

import numpy as np
import pandas as pd

# ================== 可調參數 ==================
NUM_VMS = 10000      # 要幾個 VM
NUM_PMS = 2000       # 要幾台 PM
RANDOM_SEED = 42
# ============================================

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# --------- 檔案位置設定 ---------
TASK_USAGE_DIR = Path("data/google_raw/task_usage")
TASK_USAGE_FILES = [
    TASK_USAGE_DIR / "part-00000-of-00500.csv.gz",
    # 如果你有多個檔案，也可以再加進來：
    # TASK_USAGE_DIR / "part-00001-of-00500.csv.gz",
]

MACHINE_EVENTS_DIR = Path("data/google_raw/machine_events")
MACHINE_EVENT_CANDIDATES = [
    MACHINE_EVENTS_DIR / "machine_events.csv.gz",
    MACHINE_EVENTS_DIR / "part-00000-of-00001.csv.gz",
]


# ================== 讀取 task_usage → VM ==================
def load_task_usage() -> pd.DataFrame:
    """
    從 Google trace 的 task_usage 讀資料，使用關鍵欄位：

    0 start_time
    1 end_time
    2 job_id
    3 task_index
    4 machine_id
    5 cpu_rate
    6 canonical_memory     （原始 canonical mem）
    7 assigned_memory      （真正分配給 VM 的記憶體）
    10 max_memory_usage    （最大 memory 使用率）

    我們稍後會用：
      - cpu_rate          → VM CPU demand
      - assigned_memory   → VM memory demand
    """
    print("🔹 讀取 task_usage ...")

    usecols = [0, 1, 2, 3, 4, 5, 6, 7, 10]
    names = [
        "start_time",
        "end_time",
        "job_id",
        "task_index",
        "machine_id",
        "cpu_rate",
        "canonical_memory",
        "assigned_memory",
        "max_memory_usage",
    ]

    frames = []
    for f in TASK_USAGE_FILES:
        f = Path(f)
        if not f.exists():
            print(f"⚠️ 找不到檔案: {f}，略過")
            continue

        print(f"  ✓ 讀取: {f}")
        df_part = pd.read_csv(
            f,
            header=None,
            compression="gzip",
            usecols=usecols,
            names=names,
        )
        frames.append(df_part)

    if not frames:
        raise FileNotFoundError("❌ 沒有任何 task_usage 檔案被讀到，請確認 TASK_USAGE_FILES")

    df = pd.concat(frames, ignore_index=True)
    print(f"  → task_usage 總列數: {len(df)}")
    return df


def build_vms_from_task_usage(df: pd.DataFrame):
    """
    從 task_usage 建立 VM 資料：

    VM key = (job_id, task_index)

    CPU demand:
        max_cpu = 此 VM 在所有時間點中的最大 cpu_rate
        cpu_demand = max_cpu * 100  （0~100）

    Memory demand:
        max_mem = 所有時間點中的最大 assigned_memory
        memory_demand = max_mem * 100 （0~100）

    都裁切在 [1, 100] 之間，單位可以視為「百分比容量」，
    讓它跟 PM 的 capacity (0~100) 對齊。
    """
    print("🔹 依 (job_id, task_index) 聚合成 VM ...")

    grouped = df.groupby(["job_id", "task_index"])

    agg = grouped.agg(
        max_cpu=("cpu_rate", "max"),
        max_mem=("assigned_memory", "max"),
    ).reset_index()

    # 去掉沒資源的 VM
    agg = agg[(agg["max_cpu"] > 0) & (agg["max_mem"] > 0)]

    total_vm_candidates = len(agg)
    print(f"  → 可用 VM 數量（unique job_id, task_index）: {total_vm_candidates}")

    # 抽樣 NUM_VMS 個
    if total_vm_candidates < NUM_VMS:
        print(f"  ⚠️ 只有 {total_vm_candidates} 個 VM，小於要求的 {NUM_VMS}，將全部使用。")
        agg_sample = agg.sample(n=total_vm_candidates, random_state=RANDOM_SEED)
    else:
        agg_sample = agg.sample(n=NUM_VMS, random_state=RANDOM_SEED)

    # CPU / Memory 轉成 0~100 scale
    cpu_demand = (agg_sample["max_cpu"] * 100.0).clip(lower=1.0, upper=100.0)
    mem_demand = (agg_sample["max_mem"] * 100.0).clip(lower=1.0, upper=100.0)

    vms = []
    for i, row in agg_sample.reset_index(drop=True).iterrows():
        vms.append(
            {
                "id": int(i),
                "job_id": int(row["job_id"]),
                "task_index": int(row["task_index"]),
                "cpu_demand": float(cpu_demand.iloc[i]),
                "memory_demand": float(mem_demand.iloc[i]),
            }
        )

    print(f"  ✓ 最終 VM 數量: {len(vms)}")
    return vms


# ================== 讀取 machine_events → PM ==================
def find_machine_events_file() -> Path:
    for cand in MACHINE_EVENT_CANDIDATES:
        if cand.exists():
            print(f"  ✓ 使用 machine_events 檔案: {cand}")
            return cand
    raise FileNotFoundError(
        f"❌ 找不到 machine_events 檔案，請確認下列其中一個存在：\n"
        + "\n".join([str(c) for c in MACHINE_EVENT_CANDIDATES])
    )


def load_machine_events() -> pd.DataFrame:
    """
    從 machine_events 讀出 PM capacity

    0 timestamp
    1 machine_id
    2 event_type
    3 platform_id（機器類型）
    4 cpu_capacity         （比例，例如 0.5）
    5 memory_capacity      （比例，例如 0.2493）

    我們會用：
      - cpu_capacity
      - memory_capacity

    最後轉成：
      cpu_capacity * 100
      memory_capacity * 100
    """
    print("🔹 讀取 machine_events ...")
    f = find_machine_events_file()

    usecols = [0, 1, 4, 5]
    names = ["timestamp", "machine_id", "cpu_capacity", "memory_capacity"]

    df = pd.read_csv(
        f,
        header=None,
        compression="gzip",
        usecols=usecols,
        names=names,
    )

    # 去掉無效的
    df = df[(df["cpu_capacity"] > 0) & (df["memory_capacity"] > 0)]

    # 依 timestamp 排序後，取每台機器最後一次紀錄（最新狀態）
    df = df.sort_values("timestamp")
    df_latest = df.drop_duplicates(subset=["machine_id"], keep="last")

    print(f"  → 不重複機器數量: {len(df_latest)}")
    return df_latest


def build_pms_from_machine_events(df_pm: pd.DataFrame):
    """
    從 machine_events 建立 PM 資料：

    cpu_capacity  = raw_cpu_capacity * 100
    memory_capacity = raw_memory_capacity * 100

    讓 scale 落在 0~100，跟 VM demand 一致。
    """
    total_pm_candidates = len(df_pm)

    if total_pm_candidates < NUM_PMS:
        print(f"  ⚠️ 只有 {total_pm_candidates} 台 PM，小於要求的 {NUM_PMS}，將全部使用。")
        df_sample = df_pm.sample(n=total_pm_candidates, random_state=RANDOM_SEED)
    else:
        df_sample = df_pm.sample(n=NUM_PMS, random_state=RANDOM_SEED)

    df_sample = df_sample.reset_index(drop=True)

    pms = []
    for i, row in df_sample.iterrows():
        cpu_cap = float((row["cpu_capacity"] * 100.0))
        mem_cap = float((row["memory_capacity"] * 100.0))
        pms.append(
            {
                "id": int(row["machine_id"]),  # 使用原本 machine_id 當作 PM id
                "cpu_capacity": cpu_cap,
                "memory_capacity": mem_cap,
            }
        )

    print(f"  ✓ 最終 PM 數量: {len(pms)}")
    return pms


# ================== 主流程 ==================
def main():
    print("=== Google Trace → 2000 PM / 10000 VM Dataset 產生器 ===")

    # 1. 讀 task_usage & 產生 VM
    df_task = load_task_usage()
    vms = build_vms_from_task_usage(df_task)

    # 2. 讀 machine_events & 產生 PM
    df_pm = load_machine_events()
    pms = build_pms_from_machine_events(df_pm)

    # 3. 輸出 JSON
    out_dir = Path("data/google_dataset")
    out_dir.mkdir(parents=True, exist_ok=True)

    vms_file = out_dir / "google_vms_10000.json"
    pms_file = out_dir / "google_pms_2000.json"

    with open(vms_file, "w", encoding="utf-8") as f:
        json.dump(vms, f, indent=2)
    with open(pms_file, "w", encoding="utf-8") as f:
        json.dump(pms, f, indent=2)

    print("\n🎉 完成！")
    print(f"   VM 檔案: {vms_file}")
    print(f"   PM 檔案: {pms_file}")


if __name__ == "__main__":
    main()
