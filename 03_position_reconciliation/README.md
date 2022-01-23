## Instructions
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