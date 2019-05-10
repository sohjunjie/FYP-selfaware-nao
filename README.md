# Awareness model for humanoid robot

## How to set up the code
### 1. Setup for the NAO robot
Move all contents in the `nao` folder into the root directory of the `NAO robot`.



### 2. Setup for the PC
#### 2.1. Install the python packages
The logic of the awareness runs on a remote device. Navigate to the `pc` in your `command prompt` and run the following command to install the required python packages.
```
$ pip install -r requirements.txt
```

#### 2.2. Troubleshooting problematic dependencies
You may face the following issues when trying to install the required dependencies. Try the following suggestions to see if the issue can be resolved.
| Dependencies | Solution |
| ------------- | ------------- |
| pip install `sutime` | [link to stackoverflow solution](https://stackoverflow.com/questions/14372706/visual-studio-cant-build-due-to-rc-exe) <br> [link to sutime full setup](https://github.com/FraBle/python-sutime) |
| pip install `cytoolz`  | install using `.whl` file <br> i.e. `pip install whl/cytoolz-0.9.0.1-cp36-cp36m-win_amd64.whl` |
| pip install `ujson`  | install using `.whl` file <br> i.e. `pip install whl/ujson-1.35-cp36-cp36m-win_amd64.whl` |


#### 2.3. Get Required API keys
API keys from the following IBM Watson services are required to run the program. Obtain your API keys from the following links and set all the required values in the `dot.env` file provided in the `pc` folder. Rename the file to simply `.env` following that.
1. Watson Tone Analyzer [link](https://cloud.ibm.com/apidocs/tone-analyzer)
2. Watson Natural Language Understanding [link](https://cloud.ibm.com/apidocs/natural-language-understanding)




## Running the code

### 1. Pre-requisite
- To successfully run the awareness model, the remote PC in which the awareness logic is executed need to have all firewall switched off
- Ensure that you train the robot with your face with the name `john`, `tom`, or `jack`. The memory of the robot is loaded with default values for the human `john` by default. 

### 2. Confirm remote PC local IP Address
- A websocket connection needs to be setup between the remote PC and the NAO robot for communication. Derive the local IP address using `ipconfig` or `ifconfig`
- As the NAO robot needs to know the IP address of the remote PC in order to establish the websocket connection, please ensure that the NAO robot communicates to the correct IP address. You should update the constant variable PC_ADDR in `nao/config.py` since the NAO robot connects to the IP address defined by this variable.

### 3. Run startup script that give access to websocket library
Execute the command `source ~/.bashrc` in the NAO robot so that NAO gain access to its websocket python library.

### 4. Finally, start running the awareness
We can start to run the awareness model in this step.
- In your remote PC, run the `ws_app.py` python script to start the `Awareness` websocket server
- In the NAO robot, run the `robot_init.py` python script. This will initialize the NAO robot, causing it to establish a connection with the `Awareness` websocket server.
The steps for running the awareness model completes at this point
