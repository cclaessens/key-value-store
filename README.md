# key-value-store

Python implementation in ``src/key_value_store.py`` using sqlite3 and thread locks. Because sqlite3 is a standard library no extra installation is required for running the test script. It is also lightweight and does not require seperate server processes. However it is limited in use cases with high concurrency.

## Tests in test_key_value_store.py

Execute test script to test basic functionality (put, get, delete), persistence (a new instance of ```KeyValueStore``` can read values stored by other instance), and speed of reading and writing on multiple threads.

Tested on Apple M1 Pro Chip (10 cores) with SSD. 
<br>Test output:

```
Size of variable: 195kB
Time taken by 5 threads to put and get 200kB values 100 times: 87 ms
Last thread to write: 1
.
Read value stored by different instance of KeyValueStore
....
Starting threads with different delays before writing to simulate write skew
Thread-6 (update_item) read value: initial
Thread-7 (update_item) read value: initial
Final value in database: value1
.
----------------------------------------------------------------------
Ran 6 tests in 1.104s

OK
```

With 87 ms for 5 threads doing 100 put and get operations each the performance meets the target of few operations per ms with values up to hundreds of kB. 

## Comments on design choices

- **SQL**: In the Project 8 experiment our slow controls software use PostgreSQL for logging all sensor readout. Choosing something lighter for a smaller scale project brought me to sqlite3, which conveniently is already a standard library in python. While I am not hugely familar with SQL, using the basic commands for this example was easy enough.
- **Database configuration**: I used the Write-Ahead Logging mode. From a quick research I learned that this way, changes are first written to a log and readers can still read the database file in the meantime. I also set synchronous setting to OFF. This way, speed is further increased at the risk of loosing data during a crash or power loss. The database itself is still persistent during a software crash.
- **multi-threading**: In the test script multiple threads are created to test parallel operations on the database. However, in Python, only one thread is allowed to execute at a time in the interpreter. In this case this may actually be an advantage because it avoids conflict for resource access, which may actually make the test faster. 
- **thread locks**: Multiple operations on the same instance or space in memory have to be prevented. The trigger software I programmed for Project 8 used multi-threading and thread safety was ensured by using std:mutex. The threading package in python provides an equivalent functionality.
- **Speed**: I implemented the KeyValueStore in Python and C++. Surprisingly I found the python tests to run faster than the C++ equivalent. The reason could be the sqlite library. I had to rebuild it for my arm chip and the built-in Python interface may just be optimized for better performance. Or the Python Global Interpreter Lock could be preventing conflicting resource access requests. 
- **Unit tests and version control**: We use both in most of the software that we develop.