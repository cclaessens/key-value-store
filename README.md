# key-value-store

Python implementation in src/key_value_store.py using sqlite3 and threading. Lock for mutual exlcusion of threads trying to access the database simultaneously. Because sqlite3 a standard library it does not need to be installed for running the test script. It is also lightweight and does not require seperate server processes. However it is limited high concurrency is required.

## Tests in test_key_value_store.py

Execute test script to test basic functionality (put, get, delete), persistence (a new instance of ```KeyValueStore``` can read values stored by other instance), and speed of reading and writing on multiple threads.

Tested on MacBookPro with M1 core. Output:

```
Size of variable: 98KB
Time taken by 5 threads to put and get 100kB values: 3.2148361206054688 ms
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
Ran 6 tests in 1.017s
```

With 3 ms for 5 threads doing one put and get each the performance is slower than the goal. This may be improved by using PostgreSQL which is more efficient at handling concurrent writing. Using C or C++ would also be faster.

