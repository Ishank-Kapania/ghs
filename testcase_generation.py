import os
import random

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

def generate_graph(n, filename):
    par = [i for i in range(n)]
    sz = [1 for _ in range(n)]
    prev_val = 1
    cnt = 0
    values_picked = [0] * 9000
    edges = []
    random.seed()
    while cnt < n - 1:
        a = random.randint(0, n-1)
        b = random.randint(0, n-1)
        if a == b:
            continue
        edge_added = merge_set(a, b, par, sz)
        cnt += edge_added
        if edge_added == 0:
            continue
        val = prev_val + 1 + random.randint(0, 4)
        values_picked[val] = 1
        edges.append((val, (a, b)))
        prev_val = val

    adjM = [[100000 for _ in range(n)] for _ in range(n)]
    for val, (a, b) in edges:
        adjM[a][b] = val
        adjM[b][a] = val

    for i in range(n):
        for j in range(i + 1, n):
            if adjM[i][j] == 100000 and random.randint(0, 1) == 0:
                for k in range(5, 9000, random.randint(1, 4)):
                    if values_picked[k] == 0:
                        adjM[i][j] = k
                        adjM[j][i] = k
                        values_picked[k] = 1
                        break

    # Write to file
    with open(filename, 'w') as f:
        f.write(f"{n}\n")
        for i in range(n):
            for j in range(n):
                f.write(f"{adjM[i][j]} ")
            f.write("\n")

def main():
    increments = int(input("How many test cases to generate with increments of 3?\n"))
    input_dir = "input"
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)

    for i in range(1,increments+1):
        n = i*3
        generate_graph(n, os.path.join(input_dir, f"{n}.txt"))

if __name__ == "__main__":
    main()
