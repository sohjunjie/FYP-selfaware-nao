# Utility commands and python scripts

#### 1. reset awareness memory database
You can reset the memory of the awareness by executing the python script `reset_db.py` located in the `pc` folder. 


#### 2. test speech recognition capability of NAO robot
You can test the NAO robot's speech recognition capability by executing the python script `robot_test_dialog.py` in the NAO robot


#### 3. test face recognition capability of NAO robot
You can test the NAO robot's face recognition capability by executing the python script `robot_test_face.py` in the NAO robot


#### 4. test face websocket connection between PC and NAO robot
To test if a websocket connection can be establish, first execute the `ws_app_test.py` script in the `pc` folder. This will establish a test websocket server. Then, execute the `robot_test_websocket.py` script in the NAO robot.


#### 3. simulate awareness logic
You can simulate the awareness program by executing the python script `robot_test.py`. Start the conversation with the command `[E]`. End the conversation with the command `[C]`.
