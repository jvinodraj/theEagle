## **1. Efficiency Factor (EF)**  
### **Definition:**  
EF measures **how much power you generate per heartbeat**, indicating aerobic efficiency.  

### **Formula:**  
$$
EF = \frac{\text{Average Power (W)}}{\text{Average Heart Rate (bpm)}}
$$

### **Benchmark Values:**  
| Runner Type  | EF (W/bpm)  |
|-------------|------------|
| Beginner   | 0.8 - 1.2  |
| Intermediate | 1.2 - 1.6  |
| Advanced   | 1.6 - 2.0  |
| Elite      | 2.0+        |

### **Interpreting Trends:**  
✔ **Increasing EF** → Improved aerobic efficiency.  
❌ **Decreasing EF** → Overtraining, fatigue, or inefficiency.  

### **Graph:**  
A line chart showing **EF trend over multiple runs** (x-axis: run index, y-axis: EF).  

![Efficiency Factor Over Time](/images/efficiency_factor_easy_runs.png)

---

## **2. Heart Rate Recovery (HRR)**  
### **Definition:**  
HRR measures how quickly your heart rate drops **after stopping exercise**, reflecting cardiovascular fitness.  

### **Formula:**  
$$
HRR = \text{HR at end of run} - \text{HR after 60 seconds}
$$

### **Benchmark Values:**  
| Fitness Level | HRR (bpm drop in 60s) |
|--------------|---------------------|
| Poor        | < 12 bpm            |
| Average     | 12 - 20 bpm         |
| Good        | 20 - 30 bpm         |
| Excellent   | 30+ bpm             |

### **Interpreting Trends:**  
✔ **Higher HRR** → Better recovery & fitness.  
❌ **Lower HRR** → Possible fatigue, overtraining, or poor conditioning.  

### **Graph:**  
A **bar chart** showing **HRR per run** (x-axis: run index, y-axis: HRR in bpm).  

---

## **3. Running Economy (RE)**  
### **Definition:**  
RE evaluates **energy efficiency in running**, linking power, pace, and oxygen consumption.  

### **Formula:**  
Running Economy is typically calculated as:

$$
RE = \frac{\text{Power Output (W)}}{\text{Pace (m/s)}}
$$

where:
- **Power Output (W):** The energy output measured in watts.  
- **Pace (m/s):** The speed of running in meters per second (converted from GPS speed). 

### **Benchmark Values:**  
| Runner Type  | RE (W·min/km)  |
|-------------|---------------|
| Beginner   | 200+          |
| Intermediate | 150 - 200    |
| Advanced   | 100 - 150     |
| Elite      | < 100         |

### **Changes & Features Added:**
✅ **Boxplot Chart for Running Economy:**  
- Shows **variation in RE** per date.
- Helps **identify outliers** and trends.

✅ **Efficiency Factor (EF) Remains Unchanged:**  
- Plotted as a **line chart** over time.

✅ **File Names for Charts:**  
- `efficiency_factor_easy_runs.png`
- `running_economy_easy_runs.png`

### **How to Interpret the Running Economy Chart:**
📌 **Lower RE:** More efficient running (less power used for given speed).  
📌 **Higher RE:** Less efficient running (more power needed).  
📌 **Tight Boxplot:** Consistent efficiency across a day.  
📌 **Wider Boxplot:** Large variability in efficiency across a day.  

This will give you deeper insights into how efficient you are running **at different speeds and power levels** over time. 

### **Graph:**  
A **scatter plot** of **RE vs. run index** to track efficiency changes.  


![Running Economy over time](/images/running_economy_aerobic_runs.png)

---

## **4. Heart Rate Drift Index (HRDI)**  
### **Definition:**  
HRDI quantifies **how heart rate increases relative to power over time**, indicating aerobic efficiency.  

### **Formula:**  

$$
HRDI = \frac{\left( \text{Avg HR (2nd Half)} - \text{Avg HR (1st Half)} \right)}{\text{Avg HR (1st Half)}} \times 100
$$

### **Benchmark Values:**  
| HR Drift (%) | Interpretation |
|-------------|---------------|
| < 3%        | Excellent Efficiency |
| 3 - 5%      | Normal Aerobic Response |
| 5 - 10%     | Possible Fatigue or Dehydration |
| 10%+        | Inefficient, Overexertion |

### **Interpreting Trends:**  
✔ **Lower HRDI** → Stable endurance.  
❌ **High HRDI** → Dehydration, overexertion, poor pacing.  

### **Graph:**  
A **line chart** of **HRDI per run** (x-axis: run index, y-axis: HRDI %).  

![Heart Rate Drift Index over time](/images/hr_drift_index_aerobic_runs.png)

