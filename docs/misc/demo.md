let me give you a quick overview of the database we're working with.
We're using the Northwind sample database to demonstrate the backend part.
It contains tables such as Orders, Customers, Products, Employees, and more—each with relevant columns like order dates, customer names, product prices, etc.
This structure allows us to showcase data quality and observability checks on real-world business data.


---


### 1. **Token API** (`/token`)

**Script:**  
_"Next, we have a secure authentication mechanism. <br>
The `/token` endpoint issues an access token, which is required for all protected API calls. <br>
This ensures only authorized users can access sensitive data."_

**Demo:**  
- Call `/token`
- Show the returned access token and explain its use for authentication.


---

### 2. **Data Quality: Table Check** (`/quality/check-table`)

**Script:**  
_"Now, let’s look at our data quality capabilities. <br>
The `/quality/check-table` endpoint allows us to check the quality of data in any table. <br>
For example, we can see how many missing values, duplicate rows, and the total row count for a given table. <br>
This helps us quickly identify data issues at a high level."_

**Demo:**  
- Call `/quality/check-table` with a sample table (e.g., `Orders`)
- Show the output: missing values per column, duplicates, row count.

---

### 3. **Data Quality: Column Check** (`/quality/check-column`)

**Script:**  
_"For more granular analysis, the `/quality/check-column` endpoint checks the quality of a specific column. <br>
It reports missing values, unique values, and—if the column is numeric—min, max, and outliers. <br>
This is useful for spotting anomalies or data entry issues in critical fields."_

**Demo:**  
- Call `/quality/check-column` with a sample table and column (e.g., `Products`, `UnitPrice`)
- Show the output: missing, unique, min, max, outliers.


---
### 4. **System Metrics API** (`/metrics/system`)

**Script:**  
_"Let’s start by showing how we can monitor the health of our backend system. <br>
This endpoint provides real-time system metrics such as CPU usage, memory, disk usage, uptime, and platform details.<br>
This helps us ensure the infrastructure is healthy and responsive."_

**Demo:**  
- Call `/metrics/system`
- Show the JSON output with CPU, memory, disk, uptime, etc.


---

## **Summary Script**

_"With these APIs, we provide robust observability and data quality checks for your data platform. You can monitor system health, ensure secure access, and quickly assess and diagnose data quality issues at both the table and column level. This empowers your team to maintain high data standards and operational reliability."_

---

**Order for Demo:**
1. `/metrics/system`
2. `/token`
3. `/quality/check-table`
4. `/quality/check-column`

