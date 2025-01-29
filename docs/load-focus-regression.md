### **Load Focus Regression Over Time**  

Load Focus (Anaerobic, High Aerobic, Low Aerobic) is based on your **Acute Training Load** (short-term workload) and **Chronic Training Load** (long-term workload). Garmin and other platforms use an **exponential decay model** to account for how training stress fades over time.  

---

### **How Load Focus Points Regress Over Time?**  
Each training session contributes to your **Load Focus** categories, but the impact decreases over time. The decay function follows:  


![Equation](https://latex.codecogs.com/png.latex?Remaining%20Load%20%3D%20Initial%20Load%20%5Ctimes%20e%5E%7B-%5Clambda%20t%7D)


Where:  
- \( λ \) is the **decay rate** (typically 0.07–0.10 per day, meaning a 7–10% loss daily).  
- \( t \) is the **time in days** after the session.  
- \( e \) is Euler’s number (≈ 2.718).  

---

### **Example: Load Regression Over a Week**  
Let’s assume:  
- You did a **High Aerobic** workout contributing **400 points** today.  
- The daily decay rate is **8% (λ = 0.08)**.  

| **Day** | **Remaining Load** (Approx.) |
|---------|-----------------------------|
| Day 0   | **400**                      |
| Day 1   | 368                          |
| Day 2   | 338                          |
| Day 3   | 311                          |
| Day 4   | 286                          |
| Day 5   | 263                          |
| Day 6   | 242                          |
| Day 7   | 223                          |

By the end of a **week**, the workout’s impact reduces to **~55% of its original value**.  

---

### **Effect on Load Balance**  
1. **Consistent Training → Stable Load Focus**  
   - If you train regularly, new workouts replace decaying points, maintaining balanced Anaerobic, High, and Low Aerobic loads.  

2. **Training Gaps → Load Drops Quickly**  
   - If you take a break, your **Acute Load drops rapidly** within days.  
   - **Chronic Load** (long-term fitness) declines more **gradually** but still trends downward.  

3. **Overloading → High Load But Risk of Overtraining**  
   - If your **Acute Load rises too fast**, Garmin may warn of **overreaching**, increasing injury risk.  

---

### **Regression and VO₂ Max**  
- **If Load Focus declines**, VO₂ Max may stagnate or drop slightly.  
- **Maintaining balanced Load Focus** helps sustain and gradually improve VO₂ Max over time.  
- A person with **VO₂ Max 84** would need **higher Load Focus targets** (e.g., 2,500+ points weekly) compared to someone with VO₂ Max 50.  
