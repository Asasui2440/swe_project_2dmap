import unittest
import os
import shutil
import tempfile
from model.map_data import MapData

class TestMapData(unittest.TestCase):
    def setUp(self):
        # Setup a temporary directory for file operations
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Test default initialization values."""
        map_data = MapData(width=10, height=8, tile_size=16)
        self.assertEqual(map_data.width, 10)
        self.assertEqual(map_data.height, 8)
        self.assertEqual(map_data.tile_size, 16)
        self.assertEqual(len(map_data.data), 8)
        self.assertEqual(len(map_data.data[0]), 10)

    def test_resize_expand(self):
        """Test resizing to a larger dimension."""
        map_data = MapData(width=5, height=5)
        # Set a specific tile at (0,0) to verify it's preserved
        map_data.set_tile_id(0, 0, 99)
        
        map_data.resize(10, 10)
        self.assertEqual(map_data.width, 10)
        self.assertEqual(map_data.height, 10)
        self.assertEqual(map_data.get_tile_id(0, 0), 99)
        # Check new area is initialized with default (assumed 0 or first tile id)
        # We don't check exact ID since it depends on default tileset, but ensure valid access

    def test_resize_shrink(self):
        """Test resizing to a smaller dimension."""
        map_data = MapData(width=10, height=10)
        map_data.set_tile_id(0, 0, 99)
        map_data.set_tile_id(9, 9, 88)
        
        map_data.resize(5, 5)
        self.assertEqual(map_data.width, 5)
        self.assertEqual(map_data.height, 5)
        self.assertEqual(map_data.get_tile_id(0, 0), 99)
        # Verify access out of bounds logic if needed, or just that data structure is correct
        with self.assertRaises(IndexError):
            _ = map_data.data[9][9]

    def test_set_get_tile(self):
        """Test setting and getting tile IDs."""
        map_data = MapData(width=5, height=5)
        success = map_data.set_tile_id(2, 2, 42)
        self.assertTrue(success)
        self.assertEqual(map_data.get_tile_id(2, 2), 42)
        
        # Test out of bounds
        success = map_data.set_tile_id(10, 10, 42)
        self.assertFalse(success)
        self.assertEqual(map_data.get_tile_id(10, 10), 0) # Fallback return value

    def test_save_and_load(self):
        """Test saving and loading map data."""
        map_data = MapData(width=5, height=5)
        map_data.set_tile_id(1, 1, 123)
        
        save_path = os.path.join(self.test_dir, "test_map.json")
        map_data.save_map(save_path)
        
        # Verify file exists
        self.assertTrue(os.path.exists(save_path))
        
        # Create new instance and load
        new_map_data = MapData()
        new_map_data.load_map(save_path)
        
        self.assertEqual(new_map_data.width, 5)
        self.assertEqual(new_map_data.height, 5)
        self.assertEqual(new_map_data.get_tile_id(1, 1), 123)

if __name__ == '__main__':
    unittest.main()
