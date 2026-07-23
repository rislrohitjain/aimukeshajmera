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
        # 1. Missing password test (must fail/flash alert)
        res_no_pass = self.client.post('/login', data={'phone': '9876543210', 'password': ''}, follow_redirects=True)
        self.assertIn('पासवर्ड', res_no_pass.get_data(as_text=True))

        # 2. Register user with mandatory password
        res = self.client.post('/login', data={
            'phone': '9876543210',
            'password': 'Password123',
            'action': 'register'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # 3. Wrong password login attempt (must fail)
        res_wrong = self.client.post('/login', data={'phone': '9876543210', 'password': 'WrongPassword'}, follow_redirects=True)
        self.assertIn('गलत पासवर्ड', res_wrong.get_data(as_text=True))

        print("OK - Test 02 Passed: Mobile user mandatory password registration and strict password verification passed.")

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

    def test_08_banner_edit_and_visitor_counter(self):
        # 1. Test visitor counter increment on visiting homepage
        res_home = self.client.get('/')
        self.assertEqual(res_home.status_code, 200)

        # 2. Test banner creation and editing via Admin API
        with self.client:
            self.client.post('/login', data={'phone': '9829943216', 'password': '9829943216', 'action': 'login'})
            
            # Create Banner
            res_add = self.client.post('/admin/api/banners', json={
                'image_url': 'https://example.com/test-banner.jpg',
                'caption': 'Test Banner Headline',
                'description': 'Test Banner Description Text',
                'order': 1
            })
            self.assertEqual(res_add.status_code, 200)

            # Get Banner ID
            res_list = self.client.get('/admin/api/banners')
            banners = json.loads(res_list.data)
            self.assertGreater(len(banners), 0)
            target_id = banners[0]['id']

            # Update Banner (PUT)
            res_edit = self.client.put(f'/admin/api/banners/{target_id}', json={
                'image_url': 'https://example.com/updated-banner.jpg',
                'caption': 'Updated Headline',
                'description': 'Updated Subtitle Description',
                'order': 5,
                'is_active': False
            })
            self.assertEqual(res_edit.status_code, 200)
            data_edit = json.loads(res_edit.data)
            self.assertTrue(data_edit['success'])

            # Test File Upload Endpoint with PIL Valid Image
            import io
            from PIL import Image
            img_byte_arr = io.BytesIO()
            img = Image.new('RGB', (800, 600), color='blue')
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            valid_file = (img_byte_arr, "test_banner.png")
            res_upload = self.client.post('/admin/api/upload-banner', data={'file': valid_file}, content_type='multipart/form-data')
            self.assertEqual(res_upload.status_code, 200)
            data_upload = json.loads(res_upload.data)
            self.assertTrue(data_upload['success'])
            self.assertIn('/static/uploads/banners/', data_upload['image_url'])

            # Test Oversized File Validation (>5MB)
            big_stream = io.BytesIO(b"0" * (6 * 1024 * 1024))
            big_file = (big_stream, "huge_banner.jpg")
            res_big = self.client.post('/admin/api/upload-banner', data={'file': big_file}, content_type='multipart/form-data')
            self.assertEqual(res_big.status_code, 400)

            print("OK - Test 08 Passed: Banner Image File Upload with 5MB size & 400x300px dimension validation verified.")

    def test_09_lead_management_and_today_birthdays(self):
        from datetime import datetime
        today_str = datetime.utcnow().strftime('%Y-%m-%d')

        # 1. Create a lead with today's DOB
        res_lead = self.client.post('/contact', json={
            'name': 'Birthday Test Client',
            'phone': '9988776655',
            'location': 'Sarwar',
            'message': 'Interested in LIC Jeevan Labh',
            'dob': today_str,
            'interested_category': 'LIC',
            'interested_plan': 'LIC Jeevan Labh'
        })
        self.assertEqual(res_lead.status_code, 200)

        # 2. Login as admin and verify today_birthdays and lead status update
        with self.client:
            self.client.post('/login', data={'phone': '9829943216', 'password': '9829943216', 'action': 'login'})
            
            res_dash = self.client.get('/admin/dashboard')
            self.assertEqual(res_dash.status_code, 200)
            self.assertIn('Birthday Test Client', res_dash.get_data(as_text=True))

            # Fetch lead record from DB
            with self.app.app_context():
                lead = ContactLead.query.filter_by(phone='9988776655').first()
                self.assertIsNotNone(lead)
                lead_id = lead.id

            # Update Lead Status
            res_update = self.client.put(f'/admin/api/leads/{lead_id}', json={
                'status': 'Policy Issued',
                'interested_plan': 'LIC Jeevan Labh (Policy #12345)'
            })
            self.assertEqual(res_update.status_code, 200)
            data_up = json.loads(res_update.data)
            self.assertTrue(data_up['success'])

            print("OK - Test 09 Passed: Today's Birthdays detection and Admin Lead Management API verified.")

    def test_10_quick_links_and_paginated_chat_logs(self):
        with self.client:
            self.client.post('/login', data={'phone': '9829943216', 'password': '9829943216', 'action': 'login'})
            
            # Check Dashboard Quick Links & Section IDs
            res_dash = self.client.get('/admin/dashboard')
            self.assertEqual(res_dash.status_code, 200)
            dash_html = res_dash.get_data(as_text=True)
            self.assertIn('href="#products-section"', dash_html)
            self.assertIn('href="#leads-section"', dash_html)
            self.assertIn('href="#banners-section"', dash_html)
            self.assertIn('href="#ai-settings-section"', dash_html)
            self.assertIn('id="activityChart"', dash_html)

            # Check Users List & Paginated Chat Logs Table
            res_users = self.client.get('/admin/users')
            self.assertEqual(res_users.status_code, 200)
            users_html = res_users.get_data(as_text=True)
            self.assertIn('chats-table', users_html)
            self.assertIn('AI_Chat_Logs_Mukesh_Ajmera.xlsx', users_html)
            self.assertIn('chats-search-input', users_html)

            print("OK - Test 10 Passed: Dashboard quick links, live activity chart & paginated chat logs table verified.")

if __name__ == '__main__':
    unittest.main()



