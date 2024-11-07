import os
import subprocess
import matplotlib.pyplot as plt

def run_command_for_file(file_path, output_dir):
    filename = os.path.basename(file_path)
    num_processes = filename.split('.')[0]
    command = f"mpiexec -n {num_processes} python ghs.py {file_path}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output_file_path = os.path.join(output_dir, filename)  # Save output with the same name as the input file
    with open(output_file_path, 'w') as f:
        f.write(result.stdout.strip())
    if result.returncode != 0:
        print(f"Error running command for {file_path}: {result.stderr}")
    time_taken = float(result.stdout.strip().split()[-1])  # Extract the time taken from the output
    return filename, time_taken

def main():
    input_dir = "input"
    output_dir = "output"
    times_file_path = os.path.join(output_dir, "times.txt")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    num_nodes = []
    times = []
    with open(times_file_path, 'w') as times_file:
        for file in os.listdir(input_dir):
            if file.endswith(".txt"):
                file_path = os.path.join(input_dir, file)
                filename, time_taken = run_command_for_file(file_path, output_dir)
                times_file.write(f"{filename}: {time_taken:.2f} seconds\n")
                num_nodes.append(int(filename.split('.')[0]))
                times.append(time_taken)
    plt.figure(figsize=(10, 6))
    bars = plt.bar(num_nodes, times, color='skyblue', edgecolor='black', linewidth=1.2)
    plt.xlabel('Number of Nodes', fontsize=14)
    plt.ylabel('Time Taken (seconds)', fontsize=14)
    plt.title('Time Taken vs Number of Nodes', fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')
    plt.xticks(num_nodes, fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.01, f'{yval:.2f}', ha='center', va='bottom', fontsize=10)
    plt.savefig('time_vs_nodes_bar.png', dpi=300)
    plt.show()

if __name__ == "__main__":
    main()
