from threading import Lock as _Lock


class ScriptableToolManager(object):
    # class properties
    _singleton_instance = None
    _lock = _Lock()

    def __new__(cls):
        # We use __new__ instead of __init__ here to get a singleton behavior
        if cls._singleton_instance is None:
            cls._singleton_instance = super(ScriptableToolManager, cls).__new__(cls)
            instance = cls._singleton_instance
            # Initiate singleton instance
            # instance.schedule = _deque()
            # instance._delegate_handle = _unreal_slate.register_slate_post_tick_callback(instance._callback)
            # PyAutomationTest.set_is_running_py_latent_command(True)

        return cls._singleton_instance
