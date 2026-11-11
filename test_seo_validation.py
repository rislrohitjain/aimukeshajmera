import os
import sys
import re
import json
import xml.etree.ElementTree as ET

# Ensure stdout handles UTF-8 on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from app import create_app
from app.database import db
from app.models import Product, Blog, User, SitemapUrl

def run_seo_tests():
    app = create_app(config_override={
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'TESTING': True
    })
    client = app.test_client()

    with app.app_context():
        db.create_all()
        # Seed test data
        p1 = Product(title='LIC Tech Term', category='LIC', description='Term plan', key_features='High cover')
        p2 = Product(title='Public Provident Fund (PPF)', category='POST_OFFICE', description='15-year plan', key_features='EEE tax free')
        b1 = Blog(title='PPF vs LIC Policy Guide', slug='ppf-vs-lic-guide', content='Comprehensive guide comparing PPF and LIC.', author='Mukesh Ajmera')
        db.session.add_all([p1, p2, b1])
        db.session.commit()

    print("[*] Testing routes and status codes...")
    routes_to_test = [
        ('/', 'Home Portal'),
        ('/about-mukesh-ajmera', 'About Page'),
        ('/lic-services-sarwar', 'LIC Services Page'),
        ('/post-office-schemes', 'Post Office Schemes Page'),
        ('/contact', 'Contact Page'),
        ('/blogs', 'Blogs Listing Page'),
        ('/blog/ppf-vs-lic-guide', 'Blog Detail Page'),
        ('/robots.txt', 'Robots.txt'),
        ('/sitemap.xml', 'XML Sitemap')
    ]

    for path, name in routes_to_test:
        res = client.get(path)
        assert res.status_code == 200, f"Route {path} failed with status {res.status_code}"
        print(f"  [OK] {name} ({path}) -> HTTP 200")

    # 1. Robots.txt Validation
    print("\n[*] Validating robots.txt...")
    robots_res = client.get('/robots.txt')
    robots_text = robots_res.get_data(as_text=True)
    assert 'User-agent: *' in robots_text, "Missing User-agent in robots.txt"
    assert 'Allow: /' in robots_text, "Missing Allow: / in robots.txt"
    assert 'Sitemap: https://aimukeshajmera.vercel.app/sitemap.xml' in robots_text, "Missing sitemap directive in robots.txt"
    print("  [OK] robots.txt is valid and points to https://aimukeshajmera.vercel.app/sitemap.xml")

    # 2. Sitemap XML Validation
    print("\n[*] Validating sitemap.xml...")
    sitemap_res = client.get('/sitemap.xml')
    assert sitemap_res.mimetype == 'application/xml', f"Incorrect sitemap mimetype: {sitemap_res.mimetype}"
    sitemap_xml = sitemap_res.get_data(as_text=True)
    root = ET.fromstring(sitemap_xml)
    urls_in_sitemap = [elem.text for elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    
    expected_urls = [
        'https://aimukeshajmera.vercel.app/',
        'https://aimukeshajmera.vercel.app/about-mukesh-ajmera',
        'https://aimukeshajmera.vercel.app/lic-services-sarwar',
        'https://aimukeshajmera.vercel.app/post-office-schemes',
        'https://aimukeshajmera.vercel.app/contact',
        'https://aimukeshajmera.vercel.app/blogs',
        'https://aimukeshajmera.vercel.app/blog/ppf-vs-lic-guide'
    ]

    for exp in expected_urls:
        assert exp in urls_in_sitemap, f"Expected {exp} in sitemap, found: {urls_in_sitemap}"
        print(f"  [OK] Sitemap contains: {exp}")

    # Ensure no old local IP addresses
    assert '172.18.' not in sitemap_xml and 'localhost' not in sitemap_xml, "Local IP / localhost found in sitemap!"
    print("  [OK] sitemap.xml verified clean with no localhost or private IPs.")

    # 3. HTML & Meta Validation on Core Pages
    print("\n[*] Validating Metadata, H1 tags, Canonical URLs, and Open Graph on HTML pages...")
    html_pages = ['/', '/about-mukesh-ajmera', '/lic-services-sarwar', '/post-office-schemes', '/contact', '/blogs', '/blog/ppf-vs-lic-guide']
    
    for path in html_pages:
        res = client.get(path)
        html = res.get_data(as_text=True)
        
        # Check title
        title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
        assert title_match and title_match.group(1).strip(), f"Missing <title> on {path}"
        title = title_match.group(1).strip()
        
        # Check meta description
        desc_match = re.search(r'<meta name="description" content="(.*?)"', html)
        assert desc_match and desc_match.group(1).strip(), f"Missing meta description on {path}"
        desc = desc_match.group(1).strip()

        # Check canonical
        canon_match = re.search(r'<link rel="canonical" href="(.*?)"', html)
        assert canon_match and canon_match.group(1).strip(), f"Missing canonical on {path}"
        canon = canon_match.group(1).strip()
        assert canon.startswith('https://aimukeshajmera.vercel.app'), f"Invalid canonical URL {canon} on {path}"

        # Check Open Graph
        assert 'property="og:title"' in html, f"Missing og:title on {path}"
        assert 'property="og:description"' in html, f"Missing og:description on {path}"
        assert 'property="og:url"' in html, f"Missing og:url on {path}"

        # Check H1 tag count (exactly 1 primary H1 per page)
        h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
        assert len(h1_matches) == 1, f"Expected exactly 1 <h1> on {path}, found {len(h1_matches)}"

        print(f"  [OK] {path}:")
        print(f"       H1: '{re.sub(r'<[^>]+>', '', h1_matches[0]).strip()[:50]}...'")
        print(f"       Title: '{title[:50]}...'")
        print(f"       Canonical: '{canon}'")

    # 4. JSON-LD Structured Data Validation
    print("\n[*] Validating JSON-LD Schema on all pages...")
    for path in html_pages:
        res = client.get(path)
        html = res.get_data(as_text=True)
        schema_blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
        assert len(schema_blocks) > 0, f"No JSON-LD schema found on {path}"
        
        for idx, block in enumerate(schema_blocks):
            try:
                schema_json = json.loads(block.strip())
                print(f"  [OK] Valid JSON-LD on {path} (block {idx+1}) - Context: {schema_json.get('@context')}")
            except Exception as e:
                print(f"  [FAIL] JSON parse error on {path}: {e}\nBlock content:\n{block}")
                raise

    # 5. Test Contact Form POST (JSON & Form data)
    print("\n[*] Validating Contact Form submission...")
    # JSON post
    res_json = client.post('/contact', json={
        'name': 'Test User',
        'phone': '9829943216',
        'location': 'Sarwar',
        'message': 'Testing contact lead'
    })
    assert res_json.status_code == 200, f"JSON contact failed: {res_json.status_code}"
    assert res_json.json['success'] is True
    print("  [OK] POST /contact (JSON) -> success")

    # Form data post
    res_form = client.post('/contact', data={
        'name': 'Form User',
        'phone': '9829943216',
        'location': 'Sarwar',
        'message': 'Testing form contact'
    }, follow_redirects=True)
    assert res_form.status_code == 200
    print("  [OK] POST /contact (Form Data) -> success")

    print("\n==========================================")
    print("ALL SEO & TECHNICAL CHECKS PASSED 100%!")
    print("==========================================")

if __name__ == '__main__':
    run_seo_tests()
