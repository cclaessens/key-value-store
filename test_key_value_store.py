import unittest
import time
import sys
import threading
import os

# import the KeyValueStore class
from src.key_value_store import KeyValueStore

class TestKeyValueStore(unittest.TestCase):
    db_path = "test_kv_store.db"  # database path to enable persistence test
    
    @classmethod
    def setUpClass(cls):
        """Create a test database file if it doesn't already exist."""
        cls.kv_store = KeyValueStore(cls.db_path)
        cls.kv_store.put("persist_key", "persist_value")  # Initial setup for persistence test
        cls.kv_store.close()  # Close the initial store instance

    @classmethod
    def tearDownClass(cls):
        """Remove the database file after all tests."""
        os.remove(cls.db_path)

    def setUp(self):
        """Setup a KeyValueStore instance for each test."""
        self.store = KeyValueStore(self.db_path)

    def tearDown(self):
        """Close KeyValueStore instance after each test."""
        self.store.close()

    def test_put_get(self):
        """Test that the store can put and get a key-value pair."""
        self.store.put("key", "value")
        self.assertEqual(self.store.get("key"), "value")

    def test_put_delete(self):
        """Test that the store can put and delete a key-value pair."""
        self.store.put("key", "value")
        self.store.delete("key")
        self.assertIsNone(self.store.get("key"))
        
    def test_update_value(self):
        """Change the value and read the most recent one."""
        key = "testkey"
        value1 = "value1"
        value2 = "value2"
        self.store.put(key, value1)
        self.store.put(key, value2)
        result = self.store.get(key)
        self.assertEqual(result, value2)
        
    def test_persistence(self):
        """Test that the store can persist data between instances."""
        
        # create a new instance of KeyValueStore
        store = KeyValueStore(self.db_path)
        # get persistent value stored by earlier instance of KeyValueStore
        self.assertEqual(store.get("persist_key"), "persist_value")
        print("\nRead value stored by different instance of KeyValueStore")
        store.close()

    def test_concurrent_get_and_put(self):
        """ Test the goal of several operations per ms with order 100s of kB value size.
            Also check that the value stored by the last thread is the one that remains"""
            
        # For keeping track of the last thread id use a mutable list
        last_thread_id = [None]
        
        # Using variables of > 100kB size
        var = "a" * 200000
        print(f"Size of variable: {round(sys.getsizeof(var) / 1024)}kB")
        
        # Define a function for the thread to run
        def put_and_get(i):
            # put and get 100 times
            for _ in range(100):
                self.store.put("key", var + str(i))
                self.store.get("key")
                
            # Update the last thread id. This is a shared variable
            last_thread_id[0] = i

        # Create 5 threads that run the put_and_get function
        threads = [threading.Thread(target=put_and_get, args=(i,)) for i in range(5)]

        # Start all the threads
        start_time = time.time()
        for thread in threads:
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        # Check that the final value is correct
        end_time = time.time()
        print(f"Time taken by {len(threads)} threads to put and get 200kB values 100 times: {round((end_time - start_time)*1e3)} ms")
        print(f"Last thread to write: {last_thread_id[0]}")
        self.assertEqual(self.store.get("key"), var + str(last_thread_id[0]))

# The assignment mentiones that for the profile of usage write skew is expected
class TestWriteSkew(unittest.TestCase):
    """New test for write skew in the KeyValueStore class."""
    db_path = 'test_kv_store.db'

    @classmethod
    def setUpClass(cls):
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        cls.store = KeyValueStore(cls.db_path)
        cls.store.put('item', 'initial')

    @classmethod
    def tearDownClass(cls):
        cls.store.close()
        os.remove(cls.db_path)

    def test_write_skew(self):
        # Simulate write skew by updating the same key in two threads with a delay
        # To prevent write skew, one would need a database setup that supports higher transaction isolation levels
        def update_item(new_value, delay=0):
            local_store = KeyValueStore(self.db_path)
            value = local_store.get('item')
            print(f"{threading.current_thread().name} read value: {value}")
            time.sleep(delay)  # Simulate delay
            local_store.put('item', new_value)
            local_store.close()

        print("\nStarting threads with different delays before writing to simulate write skew")
        thread1 = threading.Thread(target=update_item, args=('value1', 1))
        thread2 = threading.Thread(target=update_item, args=('value2', 0))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        # Reload the value from the database
        final_value = self.store.get('item')
        print("Final value in database:", final_value)
        self.assertIn(final_value, ['value1', 'value2'], "Final value should be one of the last written values.")

if __name__ == '__main__':
    unittest.main()