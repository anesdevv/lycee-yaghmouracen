import database.db as db

class AuthService:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AuthService, cls).__new__(cls, *args, **kwargs)
            cls._instance.current_user = None
        return cls._instance
        
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
        
    def login(self, username, raw_password):
        """Authenticate user and store session state."""
        if db.verify_admin(username, raw_password):
            self.current_user = username
            return True
        return False
        
    def logout(self):
        """Clear active user session."""
        self.current_user = None
        
    def is_authenticated(self):
        """Check if a session is currently active."""
        return self.current_user is not None
