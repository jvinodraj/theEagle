### **Formula for Load Focus Points Regression**  

Your **training load focus points** (anaerobic, high aerobic, and low aerobic) **decay over time** due to fitness detraining. Garmin typically follows an **exponential decay model**, meaning older training sessions contribute less to your load score.  

The **exponential decay formula** is:  

$$L_t = L_0 \times e^{-kt}$$

where:  
- \(L_t\) = Load at time \(t\)  
- \(L_0\) = Initial load (starting value)  
- \(k\) = Decay rate constant (depends on activity type)  
- \(t\) = Days since the training session  
- \(e\) = Euler's number (~2.718)  

---

### **Garmin's Approximate Decay Rates**  
Different training zones decay at different rates:  
- **Anaerobic Load:** \(k \approx 0.15\) per day (faster decay)  
- **High Aerobic Load:** \(k \approx 0.10\) per day  
- **Low Aerobic Load:** \(k \approx 0.07\) per day (slower decay)  

---

### **Example of Your Load Decay Over Time**  

#### **Day 0 (Today):**  
- Anaerobic = **329**  
- High Aerobic = **840**  
- Low Aerobic = **918**  

#### **Day 3 (After 3 days of no training):**  
Using the formula:  

$$L_3 = L_0 \times e^{-k(3)}$$

- **Anaerobic:**  
  $$329 \times e^{-0.15 \times 3} = 329 \times e^{-0.45} \approx 213$$
- **High Aerobic:**  
  $$840 \times e^{-0.10 \times 3} = 840 \times e^{-0.30} \approx 620$$
- **Low Aerobic:**  
  $$918 \times e^{-0.07 \times 3} = 918 \times e^{-0.21} \approx 737$$

#### **Day 7 (After a week of no training):**  
- **Anaerobic:**  
  $$329 \times e^{-0.15 \times 7} \approx 111$$
- **High Aerobic:**  
  $$840 \times e^{-0.10 \times 7} \approx 412$$
- **Low Aerobic:**  
  $$918 \times e^{-0.07 \times 7} \approx 595$$

---

### **Key Observations:**  
1. **Anaerobic Load drops the fastest** (within a week, it's down to ~33%).  
2. **High Aerobic Load declines at a moderate rate.**  
3. **Low Aerobic Load sustains the longest.**  

If you **stop training for 2+ weeks**, your anaerobic fitness will drop **significantly**, while your endurance (low aerobic) will remain longer but still decline.  

---

### **How to Maintain Load Balance?**  
- **Anaerobic Workouts (Intervals/Sprints) → Every 3–4 days** to prevent rapid loss.  
- **High Aerobic (Threshold Runs) → 1–2 times per week** to sustain gains.  
- **Low Aerobic (Long Runs) → At least once per week** to maintain endurance base.  
