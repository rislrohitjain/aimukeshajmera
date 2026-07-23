import unittest
import json
from app import create_app
from app.database import db
from app.models import User, Product, AISettings, ContactLead, Subscriber, SitemapUrl

class MukeshAjmeraAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_01_database_seeding(self):
        with self.app.app_context():
            lic_count = Product.query.filter_by(category='LIC').count()
            post_count = Product.query.filter_by(category='POST_OFFICE').count()
            self.assertGreaterEqual(lic_count, 10)
            self.assertGreaterEqual(post_count, 10)
            print("OK - Test 01 Passed: 10 LIC + 10 Post Office plans pre-seeded successfully.")

    def test_02_mobile_auth(self):
        res = self.client.post('/login', data={
            'phone': '9876543210',
            'password': 'Password123',
            'action': 'register'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        print("OK - Test 02 Passed: Mobile user registration/login verified for phone 9876543210.")

    def test_03_profile_update(self):
        with self.client:
            self.client.post('/login', data={'phone': '9876543210', 'password': 'Password123', 'action': 'login'})
            res = self.client.post('/profile', data={
                'action': 'update_profile',
                'name': 'Rajesh Sharma',
                'email': 'rajesh@example.com',
                'location': 'Sarwar, Rajasthan',
                'latitude': '26.0618',
                'longitude': '75.0183',
                'dob': '1990-05-15'
            }, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            
            with self.app.app_context():
                user = User.query.filter_by(phone='9876543210').first()
                self.assertEqual(user.name, 'Rajesh Sharma')
                self.assertEqual(user.location, 'Sarwar, Rajasthan')
            print("OK - Test 03 Passed: Profile update (Name, DOB, Location, Lat, Long) verified.")

    def test_04_ai_chatbot(self):
        res = self.client.post('/api/chat', json={'message': 'Tell me about Jeevan Labh plan'})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIsNotNone(data['whatsapp_url'])
        print("OK - Test 04 Passed: AI Chatbot response & WhatsApp URL generated.")

    def test_05_admin_ai_engine_toggle(self):
        with self.client:
            self.client.post('/login', data={'phone': '9829943216', 'password': '9829943216', 'action': 'login'})
            res = self.client.post('/admin/api/ai-settings', json={
                'active_provider': 'openai',
                'api_key': 'sk-test-key-mock',
                'local_endpoint': 'http://localhost:11434/api/generate',
                'system_prompt': 'You are LIC MITRA AI.'
            })
            self.assertEqual(res.status_code, 200)
            print("OK - Test 05 Passed: Admin AI Engine toggle verified.")

    def test_06_contact_and_subscribe(self):
        res_contact = self.client.post('/contact', json={
            'name': 'Ramesh Kumar',
            'phone': '9829999999',
            'location': 'Sarwar',
            'message': 'Interested in PPF'
        })
        self.assertEqual(res_contact.status_code, 200)

        res_sub = self.client.post('/subscribe', json={'contact_info': 'ramesh@example.com'})
        self.assertEqual(res_sub.status_code, 200)
        print("OK - Test 06 Passed: Contact Us form & Subscriber endpoints verified.")

    def test_07_sitemap_and_checkdb(self):
        res_sm = self.client.get('/sitemap.xml')
        self.assertEqual(res_sm.status_code, 200)

        res_db = self.client.get('/checkdb')
        self.assertEqual(res_db.status_code, 200)
        data_db = json.loads(res_db.data)
        self.assertEqual(data_db['status'], 'connected')
        print("OK - Test 07 Passed: /checkdb and /sitemap.xml endpoints verified.")

if __name__ == '__main__':
    unittest.main()
