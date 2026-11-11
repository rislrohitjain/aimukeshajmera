import os
from dotenv import load_dotenv

# Load local environment overrides if present (.env.local), else load default production config (.env)
if os.path.exists(".env.local"):
    load_dotenv(".env.local", override=True)
else:
    load_dotenv(override=False)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "mukesh_ajmera_lic_post_office_secret_key_2026")
    
    LOCAL_DB_URL = "postgresql://postgres:Admin%40123@localhost:5432/aimukeshajmera"
    NEON_DB_URL = "postgresql://neondb_owner:npg_DYXMv5B0glPq@ep-blue-hall-ang445o4-pooler.c-6.us-east-1.aws.neon.tech/aimukeshajmera?sslmode=require"
    
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", NEON_DB_URL)
    
    if "Admin@123@localhost" in SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("Admin@123@localhost", "Admin%40123@localhost")

    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql+psycopg2://", 1)
    elif SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgresql://") and not SQLALCHEMY_DATABASE_URI.startswith("postgresql+"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgresql://", "postgresql+psycopg2://", 1)
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Business Branding Info (Smart Advisory in Hindi)
    BUSINESS_NAME = "Mukesh Ajmera LIC & Post Office"
    BUSINESS_NAME_HI = "मुकेश अजमेरा एलआईसी & पोस्ट ऑफिस"
    OWNER_NAME = "Mukesh Ajmera"
    CONTACT_PHONE = "+91 98299 43216"
    WHATSAPP_NUMBER = "919829943216"
    ADDRESS = "Near Bhimeshwar Mahadev, Dada Badi Ke Pass, Sarwar, Rajasthan 305403"
    CATCHPHRASE = "एलआईसी एवं भारत डाक बचत योजनाओं के लिए स्मार्ट वित्तीय परामर्श"
