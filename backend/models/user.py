from pymongo import MongoClient
import certifi
from datetime import datetime
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

class User:
    def __init__(self):
        self.client = MongoClient(
            os.getenv('MONGO_URI', 'mongodb+srv://medscan:MedScan@medscan.d6wgjyi.mongodb.net/medscan_auth?retryWrites=true&w=majority&appName=MedScan'),
            tlsCAFile=certifi.where()
        )
        self.db = self.client[os.getenv('MONGO_DATABASE', 'medscan_auth')]
        self.users_collection = self.db.users
        
    def create_user(self, name, email, password):
        """Create a new user"""
        # Check if user already exists
        if self.users_collection.find_one({'email': email}):
            return {'success': False, 'message': 'User already exists'}
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user document
        user_doc = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True,
            'last_login': None
        }
        
        # Insert user
        result = self.users_collection.insert_one(user_doc)
        
        return {
            'success': True,
            'user_id': str(result.inserted_id),
            'message': 'User created successfully'
        }
    
    def authenticate_user(self, email, password):
        """Authenticate user credentials"""
        user = self.users_collection.find_one({'email': email})
        
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        if not user.get('is_active', True):
            return {'success': False, 'message': 'Account is inactive'}
        
        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Update last login
            self.users_collection.update_one(
                {'_id': user['_id']},
                {'$set': {'last_login': datetime.utcnow()}}
            )
            
            return {
                'success': True,
                'user': {
                    'id': str(user['_id']),
                    'name': user['name'],
                    'email': user['email'],
                    'created_at': user['created_at'],
                    'last_login': datetime.utcnow()
                }
            }
        else:
            return {'success': False, 'message': 'Invalid password'}
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            user = self.users_collection.find_one({'_id': user_id})
            if user:
                return {
                    'success': True,
                    'user': {
                        'id': str(user['_id']),
                        'name': user['name'],
                        'email': user['email'],
                        'created_at': user['created_at'],
                        'last_login': user.get('last_login')
                    }
                }
            else:
                return {'success': False, 'message': 'User not found'}
        except:
            return {'success': False, 'message': 'Invalid user ID'}
    
    def update_user(self, user_id, update_data):
        """Update user information"""
        try:
            # Remove sensitive fields from update_data
            if 'password' in update_data:
                update_data['password'] = bcrypt.hashpw(
                    update_data['password'].encode('utf-8'), 
                    bcrypt.gensalt()
                )
            
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.users_collection.update_one(
                {'_id': user_id},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                return {'success': True, 'message': 'User updated successfully'}
            else:
                return {'success': False, 'message': 'No changes made'}
        except:
            return {'success': False, 'message': 'Failed to update user'}
    
    def delete_user(self, user_id):
        """Delete user (soft delete - set inactive)"""
        try:
            result = self.users_collection.update_one(
                {'_id': user_id},
                {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                return {'success': True, 'message': 'User deleted successfully'}
            else:
                return {'success': False, 'message': 'User not found'}
        except:
            return {'success': False, 'message': 'Failed to delete user'}
    
    def get_all_users(self):
        """Get all users (for admin purposes)"""
        try:
            users = []
            for user_doc in self.users_collection.find({}, {'password': 0}):  # Exclude password field
                users.append({
                    'id': str(user_doc['_id']),
                    'name': user_doc['name'],
                    'email': user_doc['email'],
                    'created_at': user_doc['created_at'],
                    'last_login': user_doc.get('last_login'),
                    'is_active': user_doc.get('is_active', True)
                })
            
            # Sort by creation date (newest first)
            users.sort(key=lambda x: x['created_at'], reverse=True)
            return users
            
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []
    
    def get_user_count(self):
        """Get total number of users"""
        try:
            count = self.users_collection.count_documents({'is_active': True})
            return count
        except Exception as e:
            print(f"Error counting users: {e}")
            return 0
    
    def close_connection(self):
        """Close database connection"""
        self.client.close()
