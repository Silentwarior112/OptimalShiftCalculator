import numpy as np
from scipy.interpolate import interp1d
import tkinter as tk
from tkinter import messagebox

# Function to calculate the optimal shift point for each gear
def calculate_optimal_shift_points(rpm_values, power_values, gear_ratios):
    results = []
    
    # Interpolate power values
    interp_func = interp1d(rpm_values, power_values, kind='cubic', fill_value="extrapolate")
    rpm_interpolated = np.arange(min(rpm_values), max(rpm_values) + 1, 1)
    power_interpolated = interp_func(rpm_interpolated)
    
    for i in range(len(gear_ratios) - 1):
        gear_ratio1 = gear_ratios[i]
        gear_ratio2 = gear_ratios[i + 1]
        
        # Calculate RPM change ratio
        rpm_change_ratio = gear_ratio2 / gear_ratio1
        
        max_mean_power = -np.inf
        optimal_rpm = None
        
        # Calculate mean power for each RPM range
        for rpm in range(max(rpm_values), min(rpm_values) - 1, -1):
            lower_bound = int(rpm * rpm_change_ratio)
            if lower_bound < min(rpm_values):
                continue
            
            rpm_range = rpm_interpolated[np.logical_and(rpm_interpolated >= lower_bound, rpm_interpolated <= rpm)]
            if len(rpm_range) == 0:
                continue
            
            mean_power = np.mean(power_interpolated[rpm_range - min(rpm_values)])
            
            if mean_power > max_mean_power:
                max_mean_power = mean_power
                optimal_rpm = rpm
        
        results.append((i + 1, optimal_rpm, max_mean_power))
    
    return results

# Function to handle the button click
def on_calculate():
    try:
        rpm_values = list(map(int, text_rpm_values.get("1.0", "end-1c").splitlines()))
        power_values = list(map(float, text_power_values.get("1.0", "end-1c").splitlines()))
        
        # Get gear ratios and filter out empty values
        gear_ratios = []
        for entry in entry_gear_ratios:
            value = entry.get().strip()
            if value:
                gear_ratios.append(float(value))
        
        if len(rpm_values) != len(power_values):
            raise ValueError("RPM and Power arrays must have the same length.")
        if len(gear_ratios) < 2:
            raise ValueError("Please enter at least 2 gear ratios.")
        
        results = calculate_optimal_shift_points(rpm_values, power_values, gear_ratios)
        
        result_text.set("\n".join([f"Shift {i} to {i+1}: Optimal RPM to shift: {optimal_rpm} RPM\nMean Power in range: {mean_power:.2f} HP"
                                   for i, optimal_rpm, mean_power in results]))
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Creating the GUI
root = tk.Tk()
root.title("Optimal Shift Point Calculator")

# Labels and Entries for user input
tk.Label(root, text="RPM values (each value in a new line):").grid(row=0, column=0, sticky="ne")
text_rpm_values = tk.Text(root, height=10, width=30)
text_rpm_values.grid(row=0, column=1)

tk.Label(root, text="Power values (each value in a new line):").grid(row=1, column=0, sticky="ne")
text_power_values = tk.Text(root, height=10, width=30)
text_power_values.grid(row=1, column=1)

tk.Label(root, text="").grid(row=2, column=0, sticky="ne")
entry_gear_ratios = [tk.Entry(root) for _ in range(10)]
for i, entry in enumerate(entry_gear_ratios):
    tk.Label(root, text=f"Gear Ratio {i+1}:").grid(row=2+i, column=0, sticky="e")
    entry.grid(row=2+i, column=1)

# Button to trigger calculation
tk.Button(root, text="Calculate Optimal Shift Points", command=on_calculate).grid(row=12, column=0, columnspan=2, pady=10)

# Label to display results
result_text = tk.StringVar()
tk.Label(root, textvariable=result_text, fg="blue").grid(row=13, column=0, columnspan=2)

# Start the GUI loop
root.mainloop()