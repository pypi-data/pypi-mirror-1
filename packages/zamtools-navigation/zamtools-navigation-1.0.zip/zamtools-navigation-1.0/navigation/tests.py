import unittest
from models import Location
from django.test.client import Client

class LocationTests(unittest.TestCase):
    def setUp(self):
        self.visible_parent = Location.objects.create(name="Visibile Parent", base_url='/visible/', target_url='/visible/', order=0)
        self.hidden_parent = Location.objects.create(name="Hidden Parent", base_url='/hidden/', target_url='/hidden/', order=10, hidden=True)

        # visible parent
        self.visible_child_a = Location.objects.create(name="Visible Child A", base_url='/visible/vis/', target_url='/visible/vis/', order=1, parent=self.visible_parent)
        self.hidden_child_a = Location.objects.create(name="Hidden Child A", base_url='/visible/hid/', target_url='/visible/hid/', order=2, hidden=True, parent=self.visible_parent)

        # hidden parent
        self.visible_child_b = Location.objects.create(name="Visible Child B", base_url='/hidden/vis/', target_url='/hidden/vis/', order=11, parent=self.hidden_parent)
        self.hidden_child_b = Location.objects.create(name="Hidden Child B", base_url='/hidden/hid/', target_url='/hidden/hid/', order=12, hidden=True, parent=self.hidden_parent)

    def tearDown(self):
        Location.delete(self.visible_parent)
        Location.delete(self.hidden_parent)
        Location.delete(self.visible_child_a)
        Location.delete(self.hidden_child_a)
        Location.delete(self.visible_child_b)
        Location.delete(self.hidden_child_b)
    
    def test_top_level(self):
        top_level = Location.top_level.all()
        self.assertEqual(list(top_level), [self.visible_parent])
    
    def test_children(self):
        children = self.visible_parent.children()
        self.assertEqual(list(children), [self.visible_child_a])
    
    def test_root_visible_parent_visible_child(self):
        root = self.visible_child_a.root()
        self.assertEqual(root, self.visible_parent)

    def test_root_visible_parent_hidden_child(self):
        root = self.hidden_child_a.root()
        self.assertEqual(root, self.visible_parent)

    def test_root_hidden_parent_visible_child(self):
        root = self.visible_child_b.root()
        self.assertEqual(root, self.visible_child_b)
    
    def test_root_hidden_parent_hidden_child(self):
        root = self.hidden_child_b.root()
        self.assertEqual(root, self.hidden_child_b)

class ContextTests(unittest.TestCase):
    def setUp(self):
        self.visible_parent = Location.objects.create(name="Visibile Parent", base_url='/visible/', target_url='/visible/', order=0)
        self.hidden_parent = Location.objects.create(name="Hidden Parent", base_url='/hidden/', target_url='/hidden/', order=10, hidden=True)

        # visible parent
        self.visible_child_a = Location.objects.create(name="Visible Child A", base_url='/visible/vis/', target_url='/visible/vis/', order=1, parent=self.visible_parent)
        self.hidden_child_a = Location.objects.create(name="Hidden Child A", base_url='/visible/hid/', target_url='/visible/hid/', order=2, hidden=True, parent=self.visible_parent)

        # hidden parent
        self.visible_child_b = Location.objects.create(name="Visible Child B", base_url='/hidden/vis/', target_url='/hidden/vis/', order=11, parent=self.hidden_parent)
        self.hidden_child_b = Location.objects.create(name="Hidden Child B", base_url='/hidden/hid/', target_url='/hidden/hid/', order=12, hidden=True, parent=self.hidden_parent)

    def tearDown(self):
        Location.delete(self.visible_parent)
        Location.delete(self.hidden_parent)
        Location.delete(self.visible_child_a)
        Location.delete(self.hidden_child_a)
        Location.delete(self.visible_child_b)
        Location.delete(self.hidden_child_b)

    def test_top_level(self):
        client = Client()
        response = client.get('/none/')
        top_locations = response.context[0]['top_locations']
        self.assertEqual(list(top_locations), [self.visible_parent])

    def test_current_none(self):
        client = Client()
        response = client.get('/none/')
        current_location = response.context[0]['current_location']
        self.assertEqual(current_location, None)

    def test_current_parent(self):
        client = Client()
        response = client.get('/visible/')
        current_location = response.context[0]['current_location']
        self.assertEqual(current_location, self.visible_parent)

    def test_current_parent_hidden(self):
        client = Client()
        response = client.get('/hidden/')
        current_location = response.context[0]['current_location']
        self.assertEqual(current_location, None)
    
    def test_current_child(self):
        client = Client()
        response = client.get('/visible/vis/')
        current_location = response.context[0]['current_location']
        self.assertEqual(current_location, self.visible_child_a)

    def test_current_child_hidden(self):
        client = Client()
        response = client.get('/visible/hid/')
        current_location = response.context[0]['current_location']
        self.assertEqual(current_location, self.visible_parent)

    def test_current_parent_hidden_child_hidden(self):
        client = Client()
        response = client.get('/hidden/hid/')
        current_location = response.context[0]['current_location']
        self.assertEqual(current_location, None)
    
    def test_current_long(self):
        client = Client()
        response = client.get('/visible/vis/something/')
        current_location = response.context[0]['current_location']
        self.assertEqual(current_location, self.visible_child_a)

    def test_current_long_hidden_child(self):
        client = Client()
        response = client.get('/visible/hid/something/')
        current_location = response.context[0]['current_location']
        self.assertEqual(current_location, self.visible_parent)

    def test_current_long_hidden_parent_hidden_child(self):
        client = Client()
        response = client.get('/hidden/hid/something/')
        current_location = response.context[0]['current_location']
        self.assertEqual(current_location, None)
