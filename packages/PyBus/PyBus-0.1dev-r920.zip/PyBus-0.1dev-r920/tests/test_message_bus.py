import unittest
from py_bus_test_base import PyBusTestBase

class TestMessageBus (PyBusTestBase):
        
    def test_can_subscribe(self):
        self.bus.subscribe("Some.Important.Event", self, self.handle_some_important_event)
        assert(self.bus.has_subscription(self, "Some.Important.Event"))

    def test_can_publish(self):
        self.message_handled = 0
        self.message_contents = ""
        self.bus.subscribe("Some.Important.Event", self, self.handle_some_important_event)
        self.bus.subscribe("Some.Other.Event", self, self.handle_some_other_event)

        self.bus.publish("Some.Important.Event", "Some message")
        
        assert(self.message_handled)
        assert(self.message_contents == "Some message")
    
    def handle_some_important_event(self, message):
        self.message_handled = 1
        self.message_contents = message

if __name__ == "__main__":
    unittest.main()
