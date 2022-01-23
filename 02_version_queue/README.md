## Instructions
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