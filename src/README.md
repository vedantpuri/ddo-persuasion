# Running the Code

Follow instructions in this README to get the code running!

## ablations.sh

### Options

| Option  | Description | Possible Value(s) | Required? |
| ------------- | ------------- | ------------- | ------------- |
| -v  | Print Script Version  | -  | No  |
| -h  | Print Script Help  | -  | No  |
| -d  | Data Path (DDO dataset) | string specifying path  | **Yes**  |
| -o  | Output File | string specifying output file name  | **Yes**  |
| -f  | Flush output | -  | No  |
| -c  | Configs to run | string specifying the config file names ("all"/xyz.json/abc.json,def.json)  | **Yes**  |

A couple of **important** notes:
- For options taking in values, no equal to sign ```=``` is needed. The value can be just specified after the space, eg. ```-c all_features.json```
- For ```-c``` if providing a comma separated list, ensure that there is no space before or after the comma
- There is a specific order that needs to be followed by the args for the script to work correctly. The order is same as top to bottom in the above table, i.e. for example, ```-f``` should always come after ```-o```, and ```-c``` should always be the last arg (because thats when the job starts running)
- It is **assumed** that the configs are placed in  ```configs/```

### Example Command
```bash
./ablations.sh -d /Users/vedantpuri/Downloads -o out.csv -f -c all
```
