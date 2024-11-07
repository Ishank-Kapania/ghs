import os

def read_and_sort_file(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()
    lines = [tuple(map(int, line.strip().split())) for line in lines]
    return sorted(lines)

def compare_files(file1, file2):
    content1 = read_and_sort_file(file1)
    content2 = read_and_sort_file(file2)
    same = content1 == content2
    print(f"Contents of '{os.path.dirname(file1)} / {os.path.basename(file1)}':")
    for line in content1:
        print(line)
    print(f"\nContents of '{os.path.dirname(file2)} / {os.path.basename(file2)}':")
    for line in content2:
        print(line)
    if same:
        print("The files are the same after sorting.\n")
    else:
        print("The files are different.\n")
        
def main(output_dir, output_kruskal_dir):
    for filename in os.listdir(output_dir):
        file1 = os.path.join(output_dir, filename)
        file2 = os.path.join(output_kruskal_dir, filename)
        if os.path.exists(file1) and os.path.exists(file2):
            compare_files(file1, file2)
        else:
            print(f"Missing comparison file for '{filename}' in either directory.")

if __name__ == "__main__":
    output_dir = 'output'   
    output_kruskal_dir = 'output_kruskal'
    main(output_dir, output_kruskal_dir)
