# AlphaGrepTakeHomeTest
Take home test for AlphaGrep consisting of 3 questions. Each question is resolved in
its own folder and has its own requirements.txt, with its own set of instructions, and
assumptions. This README.md consolidates all the instructions in a succinct format below,
though each of the folders contain their own README.md that have the instructions.

The repository is TEMPORARILY public for the evaluation of this assignment (I hate sharing
zip files over the email as a developer), and would be turned to PRIVATE once I get a 
confirmation on the email, or within 7 (seven) days of the submission, so that the answers
and the questions do not get leaked

<hr>

## Instructions
<hr>

### Downloader Framework

The assumption here is that the configuration would be provided on the command line,
though there is a provision of making a JSON file consisting of key/values that will be
parsed for taking the parameters to run the script. 

There is another assumption, since the 4th point in the question states a "Time Window".
The assumption is that this script will run perpetually, and when the time window hits, take
all that is needed. Then till the time window ends, in an "interval" time period check for
stat changes and fetch in any modified files.

Again, since the question deals with SSH, the assumption is that I cannot use "rsync". In
an ideal scenario, using an rsync with a git shell or WSL would be the best solution to this
problem since that is more efficient than SFTP.

Also, a better way to implement this would be to use python Watchdog as a service (or even
as a standalone script) to poll the folder from the server then rsync and or push to the
machine. Watchdog has a better "on_create()" and "on_modified()" folder that can feed into
a callback. Trying to poll from the client would mean establishing an SFTP connection and
polling it there.

We could also fire a remote command for the watchdog to keep polling the folder from the
client side script, but that complicates things from a code maintenance standpoint.

Script requires pysftp for the sftp operations. Before running script, please run
```python.exe -m pip install -r 01_downloader_framework/requirements.txt```

1. Run the file by executing (python 3 required since f-strings are used!)
    ```python.exe 01_downloader_framework/main.py -i <ip_address> -u <username> -p <password> -s <source_path> -d <destination_path> -t <time_in_24_hr_format-end_time_period>```
    assuming your working directory is "AlphaGrepTakeHomeTest"
2. ```-t``` parameter is also optional, if not provided, the script starts running immediately. When provided without a "-"
it will default run for 1 hour. Else, the "-" will be split upon by the code to get start and end times.
3. ```-j <path_to_json_file>``` one can use the -j parameter to pass in a JSON file with the keys and values
    as 
```
{
   "ip_address": "127.0.0.1",
   "username" : "osama",
   "password": "some_random_password",
   "time_window": "15:51-16:46",
   "source_path": "/home/osama/Downloads",
   "destination_path": "C:\\Users\\iqbal\\New Folder"
}
```

<hr>

### Version Queue

There are 3 different ways this queue can be made, and all three modes are in the script.
Taking inspiration from classic compression algorithms and their modes, since there is no
'one-size-fits-all', we optimise for different sets (such as in compression, some might
need faster compress, some might need faster decompression, while others might need some
middle group based tweak). Therefore, even though there is a bonus for not replicating
the queue, I will implement both the ways, that replicating the queue and without it.

Therefore, the modes that this version queue runs in are:
1. COMPUTE (default): This mode computes the operations and hence, takes up less space (both
in memory in disk), but the tradeoff is that we spend compute cycles on it.
<br><br>
    Process the queue with compute based helper function. Hence, if we encounter "Print" operations,
    we will compute the parameters and print them. Logic is quite simple. Just reverse the operations.
    Having said that the "d" operation does not contain the element which was in the lead, hence,
    every time we "dequeue" we create a modified args which contains the element that was dequeued. Then, every time
    we encounter a "p" we slice the array unto the state, and for every "e" we pop from the array, and for every "d",
    we insert the element to the front of the array.


3. DISK: The entire queue is serialised and saved on disk. This is good when S3 bucket disk
space is super cheap, and can store large objects. Requires replication of the queue.
4. MEMORY: This is a compromise between DISK and COMPUTE. Not that fast, 
but not that slow either. Again, requires replication of the queue.


1. Run the file by executing (python 3 required since f-strings are used!)
    ```python.exe 02_version_queue/main.py <number_of_inputs>```
    assuming your working directory is "AlphaGrepTakeHomeTest". 
2. Then add the number of operations, followed by the operations on the screen.
3. There is also a unit test using the ```unittest``` in-built library, that contains the 
"helper" program that the email needed in order to run the script. Also, this demonstrates
grasp on Unit Tests and the like, hence, did not add Unit Tests for other programs

<hr>


### Position Reconciliation

This one has only one assumption. The assumption is that the id_rsa file is ```Problem3\id_rsa```
for password-less login. I've tested this on WSL machine, and it works with my username ```osama```.
Therefore, the code does contain a "hard-coded" ```username='osama``` and ```private_key=Problem3\id_rsa```

The other most important thing is that this needs ```pandas>1.4.0``` (fulfilled with requirements.txt)
since that version has a callable for ```bad_lines``` which is there in one of the summary files.

Script requires pysftp for the sftp operations. Before running script, please run
```python.exe -m pip install -r 03_position_reconciliation/requirements.txt```

1. Run the file by executing (python 3 required since f-strings are used!)
    ```python.exe 03_position_reconciliation/main.py -n <name> -c <config_file> -d <directory_file> -s <summary1,summary2,summary3>```
    assuming your working directory is "AlphaGrepTakeHomeTest".