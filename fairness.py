import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def load_vehicle_counts(filename):
    # Load the CSV file, skipping the first row with units
    df = pd.read_csv(filename)
    
    # Print column names to inspect
    print("Columns in CSV file:", df.columns.tolist())
    
    # Ensure 'timestamp' column is an integer
    if 'timestamp' in df.columns:
        df['timestamp'] = df['timestamp'].astype(int)
    else:
        raise KeyError("The expected 'timestamp' column was not found. Please check the CSV file.")
    
    # Drop the 'Total Count' column if it exists
    if 'Total Count' in df.columns:
        df = df.drop(columns=['Total Count'])
    
    # Group by seconds and calculate the average vehicle count for each lane
    df = df.groupby('timestamp').mean().reset_index()
    
    return df

def generate_green_light_report(green_light_intervals):
    num_lanes = green_light_intervals.shape[1]
    report = []
    current_lane = -1
    duration = 0

    for t in range(len(green_light_intervals)):
        for lane in range(num_lanes):
            if green_light_intervals[t, lane] == 1:
                if lane == current_lane:
                    duration += 1
                else:
                    if current_lane != -1:
                        report.append(f"Lane {current_lane + 1} had green light for {duration} seconds.")
                    current_lane = lane
                    duration = 1
                break
    
    # Append the last recorded duration
    if current_lane != -1:
        report.append(f"Lane {current_lane + 1} had green light for {duration} seconds.")

    return report

def main():
    filename = 'C:/Users/manya/Desktop/cctv/Data2.csv'  # Path to your actual file
    df = load_vehicle_counts(filename)
    
    # Print the original vehicle counts table
    print("\nOriginal vehicle counts table:\n", df.values)
    
    # Rate of vehicle count change
    vehicle_change_rate = 1  # 1 vehicle per 2 seconds

    # Minimum green light duration
    min_green_light_duration = 8

    # Fairness condition: max cycles before forcing rotation
    max_cycles_before_rotation = 2

    # To track green light intervals
    num_lanes = df.shape[1] - 1  # Subtract 1 for the timestamp column
    num_seconds = df.shape[0]
    green_light_intervals = np.zeros((num_seconds, num_lanes))

    # Green light duration tracking and rotation counters
    green_light_remaining = [0] * num_lanes
    rotation_counter = [0] * num_lanes

    # Iterate through the time intervals
    for t in range(num_seconds):
        # Decrease the green light remaining time for all lanes
        for i in range(num_lanes):
            if green_light_remaining[i] > 0:
                green_light_remaining[i] -= 1

        # If any lane still has green light duration left, continue giving green light to it
        if any(duration > 0 for duration in green_light_remaining):
            max_lane_index = np.argmax(green_light_remaining)
            green_light_intervals[t, max_lane_index] = 1
        else:
            # Otherwise, select a lane based on vehicle counts, but with fairness rotation
            current_counts = df.iloc[t].values[1:]  # Skip the timestamp column
            
            # Check for lanes that haven't had green light for max_cycles_before_rotation
            eligible_lanes = [i for i in range(num_lanes) if rotation_counter[i] < max_cycles_before_rotation]
            
            if eligible_lanes:
                # Among eligible lanes, pick the one with the highest vehicle count
                max_lane_index = eligible_lanes[np.argmax(current_counts[eligible_lanes])]
            else:
                # If all lanes have had green light recently, reset counters and pick the highest count lane
                rotation_counter = [0] * num_lanes
                max_lane_index = np.argmax(current_counts)

            # Assign green light and set duration
            green_light_intervals[t, max_lane_index] = 1
            green_light_remaining[max_lane_index] = min_green_light_duration
            rotation_counter[max_lane_index] += 1

        # Update vehicle counts
        if t < num_seconds - 1:
            df.iloc[t + 1, max_lane_index + 1] = max(0, df.iloc[t + 1, max_lane_index + 1] - vehicle_change_rate)
            # Increase vehicle count for the other lanes
            for lane in range(num_lanes):
                if lane != max_lane_index:
                    df.iloc[t + 1, lane + 1] = df.iloc[t + 1, lane + 1] + vehicle_change_rate

    # Print the updated vehicle counts table
    print("\nUpdated vehicle counts table:\n", df.values)

    # Print the green light intervals
    print("\nGreen light intervals:\n", green_light_intervals)

    # Generate and print the green light report
    report = generate_green_light_report(green_light_intervals)
    for line in report:
        print(line)
    # Plot the vehicle counts for each lane separately

if __name__ == "__main__":
    main()
