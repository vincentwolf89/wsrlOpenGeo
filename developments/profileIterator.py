import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Sample elevation profile data in a Pandas DataFrame (replace with your actual data)
data = {'distance': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        'elevation': [1.0, 1.5, 1.0, 1.8, 1.6, 1.9, 1.7, 2.1, 2.8, 3.2]}
elevation_df = pd.DataFrame(data)

# Predefined dike profile points (distance, elevation)
dike_profile_points = [(0, 0.1), (1, 2), (2, 2), (3, 0.1)]  # Example points

def interpolate_elevation(distance_offset):
    return np.interp(distance_offset, elevation_df['distance'], elevation_df['elevation'])

def check_dike_fit(start_position):
    for point in dike_profile_points:
        distance_offset = point[0] + start_position
        elevation_check = interpolate_elevation(distance_offset)
        
        if point[1] > elevation_check:
            return False
    return True

fit_iterations = []  # To store fit iterations for visualization

start_position = 0
found_fit = False

while start_position <= elevation_df['distance'].max():
    fit_iterations.append(start_position)  # Store the current iteration for visualization
    
    if check_dike_fit(start_position):
        end_position = start_position + dike_profile_points[-1][0]
        print(f"Dike profile fits from position {start_position:.2f} meters to position {end_position:.2f} meters.")
        found_fit = True
        break
    else:
        start_position += 0.1

if not found_fit:
    print("No suitable fit found for the dike profile.")

plt.plot(elevation_df['distance'], elevation_df['elevation'], label='Elevation Data')

for iteration in fit_iterations:
    dike_x = [point[0] + iteration for point in dike_profile_points]
    dike_y = [point[1] for point in dike_profile_points]
    plt.plot(dike_x, dike_y, color='grey', linestyle='dotted', alpha=0.5)

if found_fit:
    dike_x = [point[0] + start_position for point in dike_profile_points]
    dike_y = [point[1] for point in dike_profile_points]
    plt.plot(dike_x, dike_y, color='green', label='Dike Profile (Fits)')
else:
    dike_x = [point[0] + start_position for point in dike_profile_points]
    dike_y = [point[1] for point in dike_profile_points]
    plt.plot(dike_x, dike_y, color='red', label='Dike Profile (Does Not Fit)')

plt.xlabel('Distance')
plt.ylabel('Elevation')
plt.legend()
plt.title('Elevation Profile with Dike Fit Visualization')
plt.show()
