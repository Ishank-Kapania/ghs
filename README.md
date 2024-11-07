# GHS Algorithm

## 1. Generating Test Cases

To generate test cases, use the following command:

```
python testcase_generation.py
```

You will be prompted to enter a number, let's say you enter 5. Then, 5 test cases will be generated (`3.txt`, `6.txt`, `9.txt`, `12.txt`, `15.txt`). Each of these files will contain graphs with the number of nodes equal to 3, 6, 9, 12, and 15, respectively. All these files will be created in a directory called `input`.

The test cases are represented as adjacency matrices, where the value of infinity is denoted by 100000. For the GHS algorithm to work, the graph should be undirected and have distinct weights for every edge.

## 2. Running GHS Algorithm

Let's say the graph is present in `input\6.txt` like this:

```
6
100000 3 7 100000 100000 100000 
3 100000 5 2 100000 100000 
7 5 100000 100000 8 100000 
100000 2 100000 100000 9 12 
100000 100000 8 9 100000 100000 
100000 100000 100000 12 100000 100000 
```

To run the GHS algorithm with verbose output, use the following command:

```
mpiexec -n 6 python ghs.py input\6.txt -v
```

If you run the algorithm using the above command with the `-v` flag, you will get all the intermediate steps that are happening in the command line.

To run the GHS algorithm without the intermediate steps, use the following command:

```
mpiexec -n 6 python ghs.py input\6.txt
```

The number of nodes in the graph should be equal to the number of processes being allocated to `mpirun`.

## 3. Generating Output for All Test Cases

To generate output for all the test cases generated in step 1, use the following command:

```
python generate_output.py
```

This will run the GHS algorithm on all text files with the number of nodes equal to `n` (name of the text file) and save the output in the `output` folder.

## 4. Generating Output for All Test Cases using Kruskal's Algorithm

To generate output for all the test cases generated in step 1 using Kruskal's algorithm, run the following command:

```
python kruskal_multiple.py
```

This will generate the output in a folder called `output_kruskal`.

## 5. Comparing Outputs

To compare the outputs in `output_kruskal` and `output` folders, use the following command:

```
python compare_multiple.py
```

This will print the corresponding files in both folders, `output` (which contains the output of GHS) and `output_kruskal` (which contains the output of Kruskal's algorithm), and compare them.