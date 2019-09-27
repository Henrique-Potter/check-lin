# OCCAM Reproducibility User-Study Experiment

In this study, you will follow the steps specified by the authors of a software prototype to reproduce the same results published in scientific work. You do not need to understand their implementation or the research, your goal is simply to follow the steps and compare the results.

# The scientific work

Researchers from the Max Planck Institute for Software Systems and the University of Pennsylvania developed an efficient algorithm  to verify Java concurrent data structures for *Linearizability*. 

*Linearizability* is a crucial correctness property for concurrent data types. Linearizability requires that the behavior of concurrently invoked operations of the data type be equivalent to the behavior in an execution where each operation takes effect at an instantaneous point of time between its invocation and return. Given an execution trace of operations, the problem of verifying its linearizability is NP-complete, and current exhaustive search tools scale poorly.
    
## Software-dependencies to execute the experiment

- Java (OpenJDK 10), Scala (2.12), Scala Build Tool, Python (3.6 or higher)

## Data sets

The experimental results check the linearizability of the history files provided in ```example/histories``` folder, which contains execution traces of different Java data structures from the  ```Java.util.concurrent``` package.

## Reproducing the results

The experiment is composed of 5 steps:

1. **Extract Data sets**: First, you need to extract the compressed file ```example/histories.zip``` into the ```example``` folder. You should have a folder named ``histories`` inside. 

2. **Creating Java Source code from the execution traces**: We now need to generate the Java source code that mimics the execution trace defined in the histories folder.
    - Execute the following command to create Java files for each trace found at ```example/histories``` (once unzipped). 

         ```
         python scripts/main.py -operation sbt_create_tests
         ```

    - This procedure should take about 1 minute.
    - This step will create the folders (produced, stat, target, project, and results) containing the necessary information to execute and compile the Java files in the next step. 
        
3. **Compiling the Java files**: After generating the Java files, it is necessary to call `sbt` to compile them as executable Java programs.
    - Execute the following command to compile the previously generated Java files. 

        ```
        python scrips/main.py -operation sbt_compile_tests
        ```
    
    - This procedure should take about 1 minute.
    - This step will create the folders (produced and stat) containing the compiled Java tests.

4. **Executing the Java programs**: Now we can execute the compiled Java files to verify the traces for linearizability.
    - Execute the following command to execute the test. 
    
        ```
        python scrips/main.py -operation java_execute_tests
        ```
    
    - This procedure should take about 4 seconds.
    - This step will populate the files from the folder `results` with data from the experiment.

    - **Reading the results**: The results are summarized in the ```results``` folder which contains three files:

        - The file ```results/table1.txt``` keeps the properties of the processed history files for each data structure which is given in **Table 1** in the paper.
        - The file ```results/table2.txt``` keeps the number of schedules generated for each data structure for increasing *d* values which is given in **Table 2** in the paper.
        - The file ```results/table3.txt``` keeps the number and percentage of the linearizable history files shown by strong gitting families of schedules for increasing *d* values which is given in **Table 3** in the paper.
       
5. **Plot the results**: Now that we have the results data, we can plot to facilitate the visualization.
    - Execute the following command.
        ```
        python scrips/main.py -operation java_execute_tests
        ```


## Notes
Before rerunning the project (e.g., via the main script) for the same set of data sets, the files produced by an earlier execution should be cleaned by:
```
$ sbt clean
```
This will avoid appending to the existing produced files.
