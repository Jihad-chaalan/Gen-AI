# debug_env.py
import os
from dotenv import load_dotenv

print("=== Environment Debug ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Files in current directory: {[f for f in os.listdir('.') if not f.startswith('.')]}")

# Try to find .env file
env_path = ".env"
if os.path.exists(env_path):
    print(f"✅ .env file found at: {env_path}")
    load_dotenv(env_path)
    
    # Check what's in the .env file
    with open(env_path, 'r') as f:
        env_content = f.read()
        print(f"📄 .env file content: {env_content}")
    
    # Check all environment variables
    print("🔍 All environment variables starting with 'G':")
    for key, value in os.environ.items():
        if key.upper().startswith('G'):
            print(f"   {key}: {value[:10]}...")  # Show first 10 chars
    
    # Try different key names
    key_names = ['Gemini_API_KEY', 'GEMINI_API_KEY', 'GOOGLE_API_KEY']
    for key_name in key_names:
        value = os.getenv(key_name)
        if value:
            print(f"✅ Found with key name: {key_name}")
            print(f"   Key value: {value[:10]}...")  # Show first 10 chars
            break
    else:
        print("❌ No Gemini API key found with common names")
        
else:
    print("❌ .env file NOT found in current directory")
    
    # Check parent directories
    parent_dir = os.path.dirname(os.getcwd())
    parent_files = [f for f in os.listdir(parent_dir) if not f.startswith('.')]
    print(f"Files in parent directory: {parent_files}")