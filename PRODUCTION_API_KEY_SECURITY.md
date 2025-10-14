# Production API Key Security Guide

## Current State (Development)

Right now, your API keys are stored in the database in **plain text**. This is fine for local development, but **NOT** safe for production.

## 🔐 Production Security Options

### Option 1: Database Encryption (Recommended - Most Balanced)

Encrypt API keys in the database using a master encryption key.

#### Implementation

**Install encryption library**:
```bash
pip install cryptography
```

**Create encryption utility** (`app/utils/encryption.py`):
```python
from cryptography.fernet import Fernet
import os
import base64

class EncryptionService:
    def __init__(self):
        # Get encryption key from environment variable
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY environment variable not set")

        # Ensure key is properly formatted
        if not key.startswith('gAAAAAB'):  # Fernet key prefix
            # If it's a base64 string, use it directly
            self.cipher = Fernet(key.encode())
        else:
            self.cipher = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string and return base64 encoded result"""
        encrypted = self.cipher.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, encrypted: str) -> str:
        """Decrypt a base64 encoded encrypted string"""
        decrypted = self.cipher.decrypt(encrypted.encode())
        return decrypted.decode()

# Singleton instance
encryption_service = EncryptionService()

# Generate a new key (run once, save to environment)
def generate_encryption_key():
    """Generate a new Fernet encryption key"""
    key = Fernet.generate_key()
    print(f"ENCRYPTION_KEY={key.decode()}")
    return key
```

**Update API Key Service** (`app/services/api_key_service.py`):
```python
from app.utils.encryption import encryption_service

class APIKeyService:
    @staticmethod
    def create_api_key(db: Session, key_data: APIKeyCreate) -> APIKey:
        """Create a new API key with encryption"""
        # Encrypt the API key before storing
        encrypted_key = encryption_service.encrypt(key_data.api_key)

        api_key = APIKey(
            name=key_data.name,
            provider=key_data.provider,
            api_key=encrypted_key  # Store encrypted
        )
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        return api_key

    @staticmethod
    def get_decrypted_api_key(db: Session, key_id: str) -> str:
        """Get and decrypt an API key"""
        api_key = db.query(APIKey).filter(APIKey.id == key_id).first()
        if not api_key:
            return None

        # Decrypt before returning
        return encryption_service.decrypt(api_key.api_key)
```

**Update Chat Service** (`app/services/chat_service.py`):
```python
from app.utils.encryption import encryption_service

class ChatService:
    @staticmethod
    def get_bot_api_key(bot: Bot) -> str:
        """Get the bot's API key (decrypted)"""
        if bot.api_key_id and bot.api_key_ref:
            # Decrypt the key from the reference
            return encryption_service.decrypt(bot.api_key_ref.api_key)
        elif bot.api_key:
            # Legacy keys might not be encrypted
            try:
                return encryption_service.decrypt(bot.api_key)
            except:
                # If decryption fails, assume it's plain text (legacy)
                return bot.api_key
        else:
            raise ValueError("No API key configured for this bot")
```

**Environment Setup**:
```bash
# Generate encryption key (run once)
python3 -c "from cryptography.fernet import Fernet; print(f'ENCRYPTION_KEY={Fernet.generate_key().decode()}')"

# Add to .env file
ENCRYPTION_KEY=your-generated-key-here
```

**Pros**:
- ✅ API keys encrypted at rest
- ✅ Single encryption key to manage
- ✅ Fast encryption/decryption
- ✅ Works with any hosting platform

**Cons**:
- ⚠️ Need to securely manage ENCRYPTION_KEY
- ⚠️ If encryption key is lost, API keys can't be decrypted

---

### Option 2: Environment Variables (Simple but Limited)

Store API keys as environment variables, reference them by name in database.

#### Implementation

**Update Database** - Store only reference names:
```python
# In api_keys table, store:
# - name: "ANTHROPIC_KEY_PROD"
# - provider: "anthropic"
# - key_env_var: "ANTHROPIC_API_KEY_1"  # Reference to env var
# - api_key: NULL
```

**Chat Service**:
```python
def get_bot_api_key(bot: Bot) -> str:
    if bot.api_key_id and bot.api_key_ref:
        # Get key from environment
        env_var = bot.api_key_ref.key_env_var
        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(f"Environment variable {env_var} not set")
        return api_key
    # ... rest of logic
```

**Environment File** (`.env`):
```bash
ANTHROPIC_API_KEY_1=sk-ant-api03-...
ANTHROPIC_API_KEY_2=sk-ant-api03-...
OPENAI_API_KEY_1=sk-...
```

**Pros**:
- ✅ Very simple
- ✅ Keys never in database
- ✅ Standard practice for secrets

**Cons**:
- ❌ Can't add keys via UI (need to update env vars and restart)
- ❌ Harder to manage multiple keys
- ❌ Less flexible for multi-tenant scenarios

---

### Option 3: AWS Secrets Manager / Azure Key Vault (Enterprise)

Use cloud provider's secrets management service.

#### AWS Secrets Manager Example

**Install SDK**:
```bash
pip install boto3
```

**Secrets Service** (`app/utils/secrets.py`):
```python
import boto3
import json
from functools import lru_cache

class SecretsManager:
    def __init__(self):
        self.client = boto3.client('secretsmanager', region_name='us-east-1')

    @lru_cache(maxsize=100)
    def get_secret(self, secret_name: str) -> str:
        """Get secret from AWS Secrets Manager (cached)"""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return response['SecretString']
        except Exception as e:
            raise ValueError(f"Failed to get secret {secret_name}: {e}")

secrets_manager = SecretsManager()
```

**Store reference in database**:
```python
# api_keys table stores:
# - name: "Production Anthropic"
# - provider: "anthropic"
# - secret_name: "ai-bot-builder/anthropic-prod"  # AWS secret name
# - api_key: NULL
```

**Retrieve in chat service**:
```python
def get_bot_api_key(bot: Bot) -> str:
    if bot.api_key_id and bot.api_key_ref:
        secret_name = bot.api_key_ref.secret_name
        return secrets_manager.get_secret(secret_name)
    # ...
```

**Pros**:
- ✅ Highly secure
- ✅ Automatic rotation support
- ✅ Audit logs
- ✅ Fine-grained access control
- ✅ Encryption at rest and in transit

**Cons**:
- ❌ More complex setup
- ❌ Costs money (though minimal)
- ❌ Tied to cloud provider
- ❌ Requires AWS/Azure credentials

---

### Option 4: HashiCorp Vault (Advanced)

Enterprise-grade secrets management with dynamic secrets.

**Pros**:
- ✅ Cloud-agnostic
- ✅ Dynamic secrets generation
- ✅ Extensive audit logging
- ✅ Fine-grained policies

**Cons**:
- ❌ Complex setup
- ❌ Requires running Vault server
- ❌ Overkill for small deployments

---

## 🎯 Recommendation by Deployment Size

### Small (1-10 clients)
**Use: Option 1 (Database Encryption)**

```bash
# Setup:
1. Install cryptography: pip install cryptography
2. Generate encryption key
3. Add to environment variables
4. Implement encryption service
5. Migrate existing keys

# Deploy to:
- Railway, Render, Fly.io with encrypted SQLite/PostgreSQL
- Set ENCRYPTION_KEY as environment variable in platform
```

### Medium (10-100 clients)
**Use: Option 1 + Environment Variables**

```bash
# Setup:
- Database encryption for user-provided keys
- Environment variables for your own service keys
- Consider switching to PostgreSQL

# Deploy to:
- Railway, Render, DigitalOcean App Platform
- Use platform's secrets management for ENCRYPTION_KEY
```

### Large (100+ clients / Enterprise)
**Use: Option 3 (Cloud Secrets Manager)**

```bash
# Setup:
- AWS Secrets Manager or Azure Key Vault
- Database stores references only
- Implement caching to reduce API calls

# Deploy to:
- AWS ECS/EKS, Azure App Service
- Use IAM roles for authentication
- Enable secret rotation
```

---

## 🚀 Quick Implementation Guide

### Step 1: Add Encryption (Recommended)

**1. Install dependencies**:
```bash
pip install cryptography
echo "cryptography>=41.0.0" >> requirements.txt
```

**2. Create encryption utility**:
```bash
# Create the file
cat > app/utils/encryption.py << 'EOF'
from cryptography.fernet import Fernet
import os

class EncryptionService:
    def __init__(self):
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY environment variable not set")
        self.cipher = Fernet(key.encode())

    def encrypt(self, plaintext: str) -> str:
        encrypted = self.cipher.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, encrypted: str) -> str:
        decrypted = self.cipher.decrypt(encrypted.encode())
        return decrypted.decode()

encryption_service = EncryptionService()
EOF
```

**3. Generate encryption key**:
```bash
python3 -c "from cryptography.fernet import Fernet; print(f'ENCRYPTION_KEY={Fernet.generate_key().decode()}')"

# Copy the output to your .env file
```

**4. Update services** (see code examples above)

**5. Migrate existing keys**:
```python
# Run once to encrypt existing keys
python3 << 'EOF'
from app.database import SessionLocal
from app.models.api_key import APIKey
from app.utils.encryption import encryption_service

db = SessionLocal()

keys = db.query(APIKey).all()
for key in keys:
    if not key.api_key.startswith('gAAAAAB'):  # Not encrypted
        key.api_key = encryption_service.encrypt(key.api_key)

db.commit()
print(f"✅ Encrypted {len(keys)} API keys")
db.close()
EOF
```

---

## 🔒 Additional Security Best Practices

### 1. Use HTTPS Always
```python
# In production, enforce HTTPS
if os.getenv('ENVIRONMENT') == 'production':
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
    )
```

### 2. Secure Database Connection
```python
# Use SSL for database connection
database_url = os.getenv('DATABASE_URL')
if 'postgresql' in database_url:
    engine = create_engine(database_url, connect_args={"sslmode": "require"})
```

### 3. Add Rate Limiting
```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/chat/{bot_id}")
@limiter.limit("10/minute")  # Max 10 requests per minute
async def chat(...):
    ...
```

### 4. API Key Rotation
```python
# Add expiry field to api_keys table
expires_at = Column(DateTime, nullable=True)

# Check expiry in chat service
if bot.api_key_ref.expires_at and bot.api_key_ref.expires_at < datetime.now():
    raise ValueError("API key has expired")
```

### 5. Audit Logging
```python
# Log API key usage
class APIKeyUsageLog(Base):
    __tablename__ = "api_key_usage"

    id = Column(String(36), primary_key=True)
    api_key_id = Column(String(36), ForeignKey('api_keys.id'))
    used_at = Column(DateTime, default=func.now())
    success = Column(Boolean)
    error_message = Column(String(255), nullable=True)
```

---

## 📋 Production Deployment Checklist

- [ ] **Encryption enabled** for API keys in database
- [ ] **ENCRYPTION_KEY** stored as environment variable (not in code)
- [ ] **HTTPS** enforced for all connections
- [ ] **Database** uses SSL connection
- [ ] **Environment variables** used for all secrets
- [ ] **.env file** added to .gitignore (never commit secrets!)
- [ ] **Rate limiting** enabled on chat endpoints
- [ ] **CORS** properly configured (not allow all origins)
- [ ] **Database backups** scheduled
- [ ] **Monitoring** set up (Sentry, LogRocket, etc.)
- [ ] **Error messages** don't expose sensitive info
- [ ] **API key expiry** implemented (optional but recommended)
- [ ] **Audit logging** for key usage (optional)

---

## 🌐 Platform-Specific Setup

### Railway
```bash
# Set environment variable in Railway dashboard
ENCRYPTION_KEY=your-key-here

# Or via CLI
railway variables set ENCRYPTION_KEY=your-key-here
```

### Render
```bash
# Add in Render dashboard under "Environment"
# Or in render.yaml:
envVars:
  - key: ENCRYPTION_KEY
    sync: false  # Don't sync to repo
```

### Fly.io
```bash
# Set secrets via CLI
fly secrets set ENCRYPTION_KEY=your-key-here
```

### DigitalOcean App Platform
```yaml
# In app.yaml
envs:
  - key: ENCRYPTION_KEY
    scope: RUN_TIME
    type: SECRET
```

### AWS Elastic Beanstalk
```bash
# Set via environment configuration
aws elasticbeanstalk update-environment \
  --environment-name my-env \
  --option-settings \
    Namespace=aws:elasticbeanstalk:application:environment,OptionName=ENCRYPTION_KEY,Value=your-key-here
```

---

## 🔐 Key Takeaways

1. **Never commit secrets to Git** - Always use environment variables
2. **Encrypt API keys in database** - Use Option 1 (database encryption)
3. **Use HTTPS in production** - Non-negotiable
4. **Single master key is enough** - ENCRYPTION_KEY in environment
5. **Keep it simple** - Start with database encryption, upgrade later if needed

---

## 📚 Summary

**For Your Use Case (Small to Medium Deployment)**:

✅ **Recommended Approach**:
- Implement database encryption (Option 1)
- Store ENCRYPTION_KEY as environment variable
- Deploy to Railway/Render/Fly.io
- Use PostgreSQL in production
- Enable HTTPS (most platforms do this automatically)

**Total Setup Time**: ~30 minutes
**Security Level**: Production-ready
**Maintenance**: Minimal

This gives you excellent security without over-engineering!
