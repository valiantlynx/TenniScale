import csv

def time_to_milliseconds(time_str):
    """Convert time in format MM:SS.SS to milliseconds."""
    minutes, seconds = time_str.split(':')
    minutes = int(minutes)
    seconds = float(seconds)
    milliseconds = (minutes * 60 + seconds) * 1000
    return int(milliseconds)

# Data as a multiline string
data = """
180
  01      00:00.14      00:00.14
  02      00:00.71      00:00.57
  03      00:01.49      00:00.78
  04      00:02.18      00:00.69
  05      00:03.04      00:00.86
  06      00:03.36      00:00.32
  07      00:03.60      00:00.24

160
  01      00:00.21      00:00.21
  02      00:01.14      00:00.93
  03      00:01.73      00:00.59
  04      00:02.19      00:00.46
  05      00:02.68      00:00.49
  06      00:03.01      00:00.33
  07      00:03.31      00:00.30
  08      00:03.51      00:00.20

140
  01      00:00.27      00:00.27
  02      00:01.09      00:00.82
  03      00:01.61      00:00.52
  04      00:02.04      00:00.43
  05      00:02.44      00:00.40
  06      00:02.78      00:00.34
  07      00:03.05      00:00.27
  08      00:03.31      00:00.26
  09      00:03.44      00:00.13
  10      00:03.63      00:00.19

120
  01      00:00.28      00:00.28
  02      00:01.02      00:00.74
  03      00:01.50      00:00.48
  04      00:01.90      00:00.40
  05      00:02.28      00:00.38
  06      00:02.62      00:00.34
  07      00:02.89      00:00.27
  08      00:03.10      00:00.21
100
  01      00:00.28      00:00.28
  02      00:00.83      00:00.55
  03      00:01.65      00:00.82
  04      00:01.97      00:00.32
  05      00:02.33      00:00.36
  06      00:02.53      00:00.20
  07      00:02.77      00:00.24
  08      00:02.92      00:00.15


80
  01      00:00.35      00:00.35
  02      00:00.95      00:00.60
  03      00:01.26      00:00.31
  04      00:01.59      00:00.33
  05      00:01.91      00:00.32
  06      00:02.22      00:00.31
  07      00:02.48      00:00.26

60
  01      00:00.66      00:00.66
  02      00:01.25      00:00.59
  03      00:01.54      00:00.29
  04      00:01.78      00:00.24
  05      00:02.01      00:00.23
  06      00:02.25      00:00.24

40
  01      00:00.28      00:00.28
  02      00:00.68      00:00.40
  03      00:00.97      00:00.29
  04      00:01.23      00:00.26
  05      00:01.42      00:00.19
  06      00:01.61      00:00.19

20
  01      00:00.28      00:00.28
  02      00:00.68      00:00.40
  03      00:00.97      00:00.29
  04      00:01.23      00:00.26
  05      00:01.42      00:00.19
  06      00:01.61      00:00.19



200
  01      00:00.27      00:00.27
  02      00:00.88      00:00.61
  03      00:02.02      00:01.14
  04      00:02.71      00:00.69
  05      00:03.14      00:00.43
  06      00:03.51      00:00.37

180

  01      00:00.48      00:00.48
  02      00:01.36      00:00.88
  03      00:02.15      00:00.79
  04      00:02.69      00:00.54
  05      00:03.14      00:00.45
  06      00:03.49      00:00.35
  07      00:03.77      00:00.28
  08      00:04.01      00:00.24
  09      00:04.22      00:00.21


160
  01      00:00.40      00:00.40
  02      00:01.07      00:00.67
  03      00:01.98      00:00.91
  04      00:02.59      00:00.61
  05      00:02.94      00:00.35
  06      00:03.24      00:00.30
140
  01      00:00.47      00:00.47
  02      00:01.14      00:00.67
  03      00:01.85      00:00.71
  04      00:02.37      00:00.52

100
  01      00:00.41      00:00.41
  02      00:01.18      00:00.77
  03      00:01.62      00:00.44
  04      00:02.01      00:00.39
  05      00:02.43      00:00.42
  06      00:02.72      00:00.29
  07      00:02.94      00:00.22
80


  01      00:00.22      00:00.22
  02      00:01.01      00:00.79
  03      00:01.48      00:00.47
  04      00:01.77      00:00.29
  05      00:02.10      00:00.33
  06      00:02.32      00:00.22
  07      00:02.65      00:00.33
60

  01      00:00.35      00:00.35
  02      00:00.89      00:00.54
  03      00:01.35      00:00.46
  04      00:01.63      00:00.28
  05      00:01.94      00:00.31
  06      00:02.22      00:00.28
40
  01      00:00.27      00:00.27
  02      00:00.78      00:00.51
  03      00:01.14      00:00.36
  04      00:01.44      00:00.30
  05      00:01.64      00:00.20
  06      00:01.80      00:00.16

20

  01      00:00.14      00:00.14
  02      00:00.55      00:00.41
  03      00:00.81      00:00.26
  04      00:01.04      00:00.23
  05      00:01.53      00:00.49

200

  01      00:00.61      00:00.61
  02      00:01.61      00:01.00
  03      00:02.31      00:00.70
  04      00:02.97      00:00.66
  05      00:03.32      00:00.35
  06      00:04.03      00:00.71
  07      00:04.24      00:00.21
  08      00:04.51      00:00.27
180
  01      00:00.61      00:00.61
  02      00:01.41      00:00.80
  03      00:02.13      00:00.72
  04      00:02.70      00:00.57
  05      00:03.03      00:00.33
  06      00:03.42      00:00.39
  07      00:03.72      00:00.30
  08      00:03.95      00:00.23
  09      00:04.17      00:00.22
  10      00:04.31      00:00.14
  11      00:04.49      00:00.18
160
  01      00:00.54      00:00.54
  02      00:01.46      00:00.92
  03      00:02.05      00:00.59
  04      00:02.51      00:00.46
  05      00:02.98      00:00.47
  06      00:03.35      00:00.37
  07      00:03.59      00:00.24
  08      00:03.83      00:00.24
140
  01      00:00.40      00:00.40
  02      00:01.38      00:00.98
  03      00:02.03      00:00.65
  04      00:02.33      00:00.30
  05      00:02.81      00:00.48
  06      00:03.14      00:00.33
  07      00:03.44      00:00.30
  08      00:03.64      00:00.20
120
  01      00:00.41      00:00.41
  02      00:01.22      00:00.81
  03      00:01.78      00:00.56
  04      00:02.14      00:00.36
  05      00:02.59      00:00.45
  06      00:02.88      00:00.29
  07      00:03.11      00:00.23
  08      00:03.34      00:00.23
  09      00:03.61      00:00.27

100
  01      00:00.48      00:00.48
  02      00:01.13      00:00.65
  03      00:01.70      00:00.57
  04      00:02.03      00:00.33
  05      00:02.34      00:00.31
  06      00:02.67      00:00.33
  07      00:02.92      00:00.25
  08      00:03.17      00:00.25
  09      00:03.39      00:00.22
80

  01      00:00.41      00:00.41
  02      00:01.10      00:00.69
  03      00:01.46      00:00.36
  04      00:01.79      00:00.33
  05      00:02.09      00:00.30
  06      00:02.35      00:00.26
  07      00:02.58      00:00.23
  08      00:02.80      00:00.22
  09      00:02.95      00:00.15
60

  01      00:00.35      00:00.35
  02      00:00.90      00:00.55
  03      00:01.18      00:00.28
  04      00:01.51      00:00.33
  05      00:01.75      00:00.24
  06      00:01.99      00:00.24
  07      00:02.13      00:00.14
40
  01      00:00.40      00:00.40
  02      00:00.82      00:00.42
  03      00:01.04      00:00.22
  04      00:01.31      00:00.27
  05      00:01.54      00:00.23
  06      00:01.68      00:00.14
  07      00:01.97      00:00.29
20
  01      00:00.34      00:00.34
  02      00:00.84      00:00.50
  03      00:01.07      00:00.23
  04      00:01.25      00:00.18
  05      00:01.51      00:00.26
"""

# Parsing the data
rows = []
lines = data.strip().split('\n')
current_height = None

for line in lines:
    line = line.strip()
    
    if line.isdigit():  # Line with just a number indicates a new height
        current_height = int(line)
    elif line:  # If the line is not empty, it has data
        parts = line.split()
        bounce_number = int(parts[0])
        total_time = parts[1]
        interval_time = parts[2]
        
        # Append parsed data as a row in the rows list
        rows.append({
            "Height": current_height,
            "Total Time (ms)": time_to_milliseconds(total_time),
            "Interval Time (ms)": time_to_milliseconds(interval_time),
            "Bounce Number": bounce_number,
            "Total Time": total_time,
            "Interval Time": interval_time
        })
        


# Writing the data to a CSV file
csv_filename = "tennis_ball_bounce_data.csv"
with open(csv_filename, mode='w', newline='') as csv_file:
    fieldnames = ["Height", "Bounce Number", "Total Time", "Interval Time", "Total Time (ms)", "Interval Time (ms)"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for row in rows:
        writer.writerow(row)

print(f"CSV file '{csv_filename}' created successfully.")


# Creating Markdown table
md_filename = "tennis_ball_bounce_data.md"
with open(md_filename, mode='w') as md_file:
    # Writing the header of the markdown table
    md_file.write("| Height | Bounce Number | Total Time | Interval Time | Total Time (ms) | Interval Time (ms) |\n")
    md_file.write("| ------ | ------------- | ---------- | ------------- | --------------- | ------------------ |\n")
    
    # Writing each row
    for row in rows:
        md_file.write(f"| {row['Height']} | {row['Bounce Number']} | {row['Total Time']} | {row['Interval Time']} | {row['Total Time (ms)']} | {row['Interval Time (ms)']} |\n")

print(f"Markdown file '{md_filename}' created successfully.")