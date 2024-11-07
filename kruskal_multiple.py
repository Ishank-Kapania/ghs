import os
def find_parent(u, par):
    if u == par[u]:
        return u
    par[u] = find_parent(par[u], par)
    return par[u]
def merge_set(u, v, par, sz):
    u = find_parent(u, par)
    v = find_parent(v, par)
    if u != v:
        if sz[u] < sz[v]:
            u, v = v, u
        par[v] = u
        sz[u] += sz[v]
        return 1
    else:
        return 0
def kruskal_algorithm(input_file_path):
    with open(input_file_path, 'r') as file:
        n = int(file.readline().strip())
        par = [i for i in range(n)]
        sz = [1 for _ in range(n)]
        edges = []
        selected_edges = []
        for i in range(n):
            row = list(map(int, file.readline().split()))
            for j in range(n):
                if j > i and row[j] < 100000:
                    edges.append((row[j], i, j))
        edges.sort()
        cnt = 0
        for weight, u, v in edges:
            if merge_set(u, v, par, sz):
                cnt += 1
                selected_edges.append((u, v, weight))
                if cnt == n - 1:
                    break
    return selected_edges
def write_output_to_file(output_directory, selected_edges, output_file_name):
    os.makedirs(output_directory, exist_ok=True)
    output_file_path = os.path.join(output_directory, output_file_name)
    with open(output_file_path, 'w') as file:
        for u, v, weight in selected_edges:
            file.write(f"{u} {v} {weight}\n")
if __name__ == "__main__":
    input_directory = 'input' 
    output_directory = 'output_kruskal'
    for input_file_name in os.listdir(input_directory):
        input_file_path = os.path.join(input_directory, input_file_name)
        if os.path.isfile(input_file_path):
            print(f"Processing {input_file_name}...")
            selected_edges = kruskal_algorithm(input_file_path)
            output_file_name = input_file_name 
            write_output_to_file(output_directory, selected_edges, output_file_name)
            print(f"Output for {input_file_name} has been saved.")
