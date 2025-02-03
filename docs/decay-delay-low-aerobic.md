# Load Focus Decay Calculation

## Formula

The **Load Focus Decay** follows an **exponential decay model**, expressed as:

$$
L(t) = L_0 \times e^{-kt}
$$

Where:

- \(L(t)\) = Load at time \(t\) (days)
- \(L_0 = 918\) (Initial Load for Low Aerobic)
- \(k = 0.245\) (Decay Rate)
- \(t\) = Number of days since the last activity
- \(e\) = Euler’s number (≈ 2.718)

## Garmin Screenshots

Here are the screenshots from Garmin illustrating the Load Focus data:

![Garmin Screenshot 1](images/Feb1.png)

![Garmin Screenshot 2](images/Feb3.jpg)

![Decay-Rate](images/Decay-rate.png)

## Calculated Values

| Day (t) | Load \(L(t)\) | Calculation \(L(t) = 918 \times e^{-0.245t}\) |
| ------- | ------------- | -------------------------------- |
| 0       | 918.00        | $$\(918 \times e^{-(0.0245 \times 0)}\)$$|
| 1       | 895.78        | $$\(918 \times e^{-(0.0245 \times 1)}\)$$|
| 2       | 874.10        | $$\(918 \times e^{-(0.0245 \times 2)}\)$$|
| 3       | 852.94        | $$\(918 \times e^{-(0.0245 \times 3)}\)$$|
| 4       | 832.30        | $$\(918 \times e^{-(0.0245 \times 4)}\)$$|

## Explanation

The **Load Focus Decay** model ensures that old training load decreases exponentially if no new training occurs. The higher the **decay rate**, the faster the load declines.

