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