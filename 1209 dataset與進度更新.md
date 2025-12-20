這是一份為您的專案 GitHub 頁面準備的 **Google Cluster Trace (2011)** 整合進度說明。這份文件的排版與內容邏輯完全依照您提供的 2024/12/09 PlanetLab 版本進行轉化，確保兩者風格一致，並補足了 Google Trace 專有的技術細節。

---

# 專案更新說明 - 2024/12/20

## 👥 給組員的說明

繼 PlanetLab 之後，我今天完成了 **Google Cluster Trace (2011)** 真實資料集的整合。這個資料集將用於專案的「工業級規模驗證」，它提供了 PlanetLab 所欠缺的**真實 PM 容量數據**，能讓我們的分配演算法（FFD, BFD, RLS-FFD）在異質性硬體環境下進行更深度的效能分析。

---

## 🆕 3. 整合 Google Cluster Trace 真實資料集

### 為什麼需要 Google Cluster Trace？

雖然 PlanetLab 是學術界的標準基準，但它存在以下局限性，我們透過整合 Google Trace 來補足：

* **補足真實 PM 容量**：PlanetLab 僅提供 CPU 使用率百分比，我們必須假設 PM 容量。Google Trace 則包含真實的  台機器的 CPU 與 Memory 容量資訊。
* **體現硬體異質性 (Heterogeneity)**：Google 資料中心包含多種不同規格的機器（不同的 CPU/RAM 比例），這能測試我們的演算法在資源不平均時的處理能力。
* **驗證工業級負載**：Google Borg 系統管理著數千萬個任務，其工作負載模式（例如「長尾分佈」和「超量預留」）更具實務代表性。

### 資料集來源

* **來源**：Google Cluster Data (GCD) v2 / 2011。
* **原始系統**：Google Borg 集群管理系統。
* **使用的子集檔案**：
* `machine_events/machine_events.csv.gz` (用於獲取 PM 容量)。
* `task_usage/part-00000-of-00500.csv.gz` (用於獲取 VM 實際需求)。



---

### Google Trace 中 VM 與 PM 的定義

#### VM 定義方式

在 Google Trace 中，工作以 `job` 為單位，每個 job 包含多個 `task`。
本研究定義：**一個 (job_id, task_index) 對應一個獨立的 VM 放置單位**。

#### VM CPU / Memory 需求計算

本專案採用 **「峰值資源需求 (Peak Demand)」** 策略進行靜態放置，以確保服務穩定性：

* **CPU 需求**：`cpu_demand = max(cpu_rate) × 100`
* **Memory 需求**：`memory_demand = max(max_memory_usage) × 100`
* **註**：我們選擇 `max_memory_usage` 而非 `assigned_memory`，是因為實際使用量更能反映裝箱的緊密度。

#### PM (Physical Machine) 容量計算

Google 對機器容量進行了 0 到 1 的標準化縮放。我們將其轉換為統一資源單位：

* **PM CPU 容量**：`cpu_capacity = raw_cpu_capacity × 100`
* **PM Memory 容量**：`memory_capacity = raw_memory_capacity × 100`

---

### 為什麼 Google Trace 需要隨機取樣？

Google Trace 原始規模極大（約  台 PM， 萬個任務）。為了實驗可行性，我們採用**隨機取樣 (Sampling)**：

1. **運算限制**：ILP 求解器無法處理萬級規模的變數，必須控制在  VM 以內才能求得精確解。
2. **靜態放置特性**：我們進行的是單一時間點的快照實驗，取樣足以代表特定負載下的分配效率。
3. **保留分佈特性**：取樣過程固定了 `random seed`，保留了 Google 工作負載中「少數大型 Job 佔據多數資源」的偏態分佈特徵。

---

### Google Trace 與 PlanetLab 的角色區分

| 項目 | PlanetLab | Google Trace (GCT) |
| --- | --- | --- |
| **資料性質** | 學術測試平台 ( simplistic ) | 真實工業級資料中心 |
| **VM 規模** | ~1,000 | 數千萬 (本專案取樣) |
| **PM 容量資料** | 無 (需假設) | **有 (真實標準化值)** |
| **Memory 指標** | 推估值 | **真實最大使用量** |
| **硬體環境** | 同質環境 | **異質環境 (多種機器類別)** |
| **主要實驗目的** | 方法論正確性驗證 | 規模化與實務魯棒性驗證 |

---

### 實驗結果初步觀察 (Google Trace)

根據我們目前的實作結果，在異質性的 Google Trace 下：

* **FFD / RLS-FFD**：表現穩定。RLS-FFD 透過隨機交換 (Swap) 成功修正了 FFD 在處理 Google 異構機器時產生的零碎空間，最終使用的 PM 數量比 FFD 少了 **~5%**。
* **BFD**：雖然嘗試緊密貼合，但在 CPU/RAM 比例差異極大的 Google PM 上，容易因某一維度先耗盡而導致放置失敗，執行時間也因計算最優殘餘空間而顯著增加。

---

### 小結

我們透過 **PlanetLab** 建立學術基準線，並使用 **Google Cluster Trace** 驗證演算法在「真實 PM 容量」與「異質資源」下的實戰能力。這種「雙資料集」的架構使本專案的實驗設計達到了學術論文級別的完整性。
