from app.database import db
from app.models import User, Product, Blog, AISettings, SitemapUrl, BannerImage

def seed_database():
    """Seeds database with 10 LIC plans, 10 Post Office plans, admin user, AISettings, Sitemap URLs, and default Banners."""
    
    # 1. Seed Admin User
    admin = User.query.filter_by(phone="9829943216").first()
    if not admin:
        admin = User(
            name="Mukesh Ajmera",
            phone="9829943216",
            email="mukeshajmera.lic@gmail.com",
            role="admin",
            location="Sarwar, Rajasthan",
            latitude=26.0618,
            longitude=75.0183,
            dob="1975-01-01"
        )
        admin.set_password("9829943216")
        db.session.add(admin)

    # 2. Seed Default Smart Advisory Settings
    ai_setting = AISettings.query.first()
    if not ai_setting:
        default_prompt = (
            "You are LIC MITRA, the intelligent Smart Financial Assistant for Mukesh Ajmera LIC & Post Office Services in Sarwar, Rajasthan.\n"
            "Owner: Mukesh Ajmera. Phone/WhatsApp: +91 9829943216.\n"
            "Address: Near Bhimeshwar Mahadev, Dada Badi Ke Pass, Sarwar, Rajasthan 305403.\n"
            "Your objective: Advise customers kindly in Hindi, English, Hinglish, Rajasthani, or Marwadi on financial investments, LIC insurance policies, and India Post savings schemes."
        )
        ai_setting = AISettings(
            active_provider="local",
            api_key="",
            local_endpoint="http://localhost:11434/api/generate",
            system_prompt=default_prompt
        )
        db.session.add(ai_setting)

    # 3. Seed Sitemap URLs (Public Indexable pages only)
    default_sitemaps = [
        {"url_path": "/", "priority": "1.0"},
        {"url_path": "/login", "priority": "0.8"},
        {"url_path": "/blogs", "priority": "0.9"}
    ]
    for sm in default_sitemaps:
        if not SitemapUrl.query.filter_by(url_path=sm["url_path"]).first():
            db.session.add(SitemapUrl(**sm))

    # Remove any existing /checkdb sitemap url entry
    old_sm = SitemapUrl.query.filter_by(url_path="/checkdb").first()
    if old_sm:
        db.session.delete(old_sm)

    # 4. Seed Default Banner Slider Images
    default_banners = [
        {
            "image_url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=1000&q=80",
            "caption": "सुरक्षित भविष्य एवं उच्च रिटर्न - मुकेश अजमेरा एलआईसी सरवाड़",
            "description": "एलआईसी जीवन सुरक्षा, पेंशन, टर्म प्लान एवं 100% टैक्स छूट के लिए अधिकृत सेवा केंद्र।",
            "order": 1
        },
        {
            "image_url": "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?auto=format&fit=crop&w=1000&q=80",
            "caption": "भारतीय डाकघर बचत योजनाएं (PPF, SSY & SCSS)",
            "description": "सुरक्षित डाकघर बचत योजनाओं की संपूर्ण जानकारी एवं खाता खोलने की निःशुल्क सुविधा।",
            "order": 2
        },
        {
            "image_url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=1000&q=80",
            "caption": "100% भारत सरकार की सुरक्षा एवं 10(10D) टैक्स छूट",
            "description": "धारा 80C के तहत आयकर बचत एवं मृत्यु/परिपक्वता पर पूर्णतः कर-मुक्त राशि।",
            "order": 3
        },
        {
            "image_url": "https://images.unsplash.com/photo-1450133064473-71024230f91b?auto=format&fit=crop&w=1000&q=80",
            "caption": "बेटियों की उच्च शिक्षा एवं विवाह हेतु सुकन्या समृद्धि योजना",
            "description": "बालिकाओं के उज्ज्वल भविष्य हेतु सर्वोच्च ब्याज दर वाली सरकारी डाकघर योजना।",
            "order": 4
        },
        {
            "image_url": "https://images.unsplash.com/photo-1573164713988-8665fc963095?auto=format&fit=crop&w=1000&q=80",
            "caption": "एलआईसी जीवन लाभ (Plan 936) - सीमित प्रीमियम एवं गारंटीड बोनस",
            "description": "कम समय प्रीमियम भरें एवं लंबे समय तक सुरक्षा व शानदार रिफंड प्राप्त करें।",
            "order": 5
        }
    ]
    for b in default_banners:
        if not BannerImage.query.filter_by(image_url=b["image_url"]).first():
            db.session.add(BannerImage(**b))

    # 5. Seed LIC Products (10 Official Plans)
    lic_plans = [
        {
            "title": "LIC Tech Term (Plan 854)",
            "category": "LIC",
            "description": "Pure non-participating online term assurance policy offering financial protection to the family in case of unfortunate demise of the policyholder.",
            "key_features": "High Sum Assured discounts | Level or Increasing Sum Assured options | Low premium rates for non-smokers | Tax benefits under Sec 80C.",
            "min_age": 18,
            "max_age": 65,
            "tax_benefits": "Sec 80C & Sec 10(10D)"
        },
        {
            "title": "LIC Jeevan Umang (Plan 945)",
            "category": "LIC",
            "description": "Whole life assurance plan offering 8% guaranteed annual survival benefit of Basic Sum Assured after premium payment term until age 99.",
            "key_features": "8% Guaranteed Annual Income after PPT | Life cover up to 100 years | Reversionary and Final Additional Bonus | Loan facility available.",
            "min_age": 0,
            "max_age": 55,
            "tax_benefits": "Sec 80C & Sec 10(10D)"
        },
        {
            "title": "LIC Jeevan Anand (Plan 915)",
            "category": "LIC",
            "description": "Double benefit plan combining financial protection against death throughout life with lump sum payout at the end of selected term.",
            "key_features": "Lump sum maturity payout | Continued life cover even after maturity | Accident benefit rider | Annual bonus addition.",
            "min_age": 18,
            "max_age": 50,
            "tax_benefits": "Sec 80C & Sec 10(10D)"
        },
        {
            "title": "LIC Nivesh Plus (Plan 849)",
            "category": "LIC",
            "description": "Single premium unit linked insurance plan (ULIP) offering life cover along with capital growth through stock market investment funds.",
            "key_features": "Single premium investment | Choice of 4 investment funds | Free fund switching | Guaranteed additions at milestones.",
            "min_age": 0,
            "max_age": 70,
            "tax_benefits": "Sec 80C & Sec 10(10D)"
        },
        {
            "title": "LIC SIIP (Plan 852)",
            "category": "LIC",
            "description": "Unit-Linked Regular Premium plan combining insurance protection and investment with guaranteed additions over policy period.",
            "key_features": "Regular premium ULIP | Guaranteed additions added to unit fund | Partial withdrawal allowed after 5 years | Flexible fund selection.",
            "min_age": 0,
            "max_age": 65,
            "tax_benefits": "Sec 80C & Sec 10(10D)"
        },
        {
            "title": "LIC Cancer Cover (Plan 905)",
            "category": "LIC",
            "description": "Non-linked specified health insurance plan offering lump sum financial protection against early and major stages of cancer.",
            "key_features": "Lump sum payout on cancer diagnosis | Premium waiver on early stage | Monthly income benefit on major stage | Fixed benefit payout.",
            "min_age": 20,
            "max_age": 65,
            "tax_benefits": "Sec 80D"
        },
        {
            "title": "LIC Jeevan Labh (Plan 936)",
            "category": "LIC",
            "description": "Limited premium paying, non-linked, with-profits endowment plan offering ideal combination of protection and savings.",
            "key_features": "Pay for limited term (e.g. 16 years pay for 25 year term) | High return with bonus additions | Loan available after 2 years | High demand plan.",
            "min_age": 8,
            "max_age": 59,
            "tax_benefits": "Sec 80C & Sec 10(10D)"
        },
        {
            "title": "LIC Bachat Plus (Plan 861)",
            "category": "LIC",
            "description": "Non-linked, hassle-free endowment savings plan with high flexibility to pay single premium or limited premium option.",
            "key_features": "Flexible premium payment modes | High sum assured rebate | Guaranteed terminal additions | Financial security for family.",
            "min_age": 0,
            "max_age": 70,
            "tax_benefits": "Sec 80C & Sec 10(10D)"
        },
        {
            "title": "LIC Jeevan Shiromani (Plan 847)",
            "category": "LIC",
            "description": "High net-worth individual (HNI) plan providing life cover and financial support for critical illnesses.",
            "key_features": "Minimum Sum Assured Rs. 1 Crore | Built-in Critical Illness cover | Guaranteed Additions @ Rs. 50 per thousand BSA | Limited PPT.",
            "min_age": 18,
            "max_age": 55,
            "tax_benefits": "Sec 80C & Sec 10(10D)"
        },
        {
            "title": "LIC Dhan Sanchay (Plan 865)",
            "category": "LIC",
            "description": "Non-linked, non-participating, individual life insurance savings plan providing guaranteed income stream during payout period.",
            "key_features": "Guaranteed income payout after PPT | Enhanced benefits for higher premiums | Death benefit payable as lump sum or installments.",
            "min_age": 3,
            "max_age": 65,
            "tax_benefits": "Sec 80C & Sec 10(10D)"
        }
    ]

    for plan in lic_plans:
        existing = Product.query.filter_by(title=plan["title"]).first()
        if not existing:
            prod = Product(**plan)
            db.session.add(prod)

    # 6. Seed Post Office Plans (10 Official Schemes)
    post_office_plans = [
        {
            "title": "Public Provident Fund (PPF)",
            "category": "POST_OFFICE",
            "description": "Sovereign guaranteed long-term government savings scheme with attractive interest rates and triple tax exemption (EEE).",
            "key_features": "15-year tenure | EEE Tax Category (Deposit, Interest & Withdrawal Tax Free) | Interest compounding annually | Partial withdrawal allowed.",
            "min_age": 0,
            "max_age": 100,
            "tax_benefits": "Sec 80C (Exempt-Exempt-Exempt)"
        },
        {
            "title": "Sukanya Samriddhi Yojana (SSY)",
            "category": "POST_OFFICE",
            "description": "Government-backed savings scheme for girl children offering the highest interest rate among small savings schemes.",
            "key_features": "High interest rate (~8.2% p.a.) | Exclusively for girl child up to 10 years | Maturity at age 21 or marriage | EEE Tax benefit.",
            "min_age": 0,
            "max_age": 10,
            "tax_benefits": "Sec 80C (EEE status)"
        },
        {
            "title": "Senior Citizen Savings Scheme (SCSS)",
            "category": "POST_OFFICE",
            "description": "Safe government savings scheme specially designed for senior citizens offering regular quarterly income.",
            "key_features": "Interest paid quarterly | High interest rate (~8.2% p.a.) | 5-year tenure extendable by 3 years | Sovereign guarantee.",
            "min_age": 60,
            "max_age": 100,
            "tax_benefits": "Sec 80C"
        },
        {
            "title": "National Savings Certificate (NSC)",
            "category": "POST_OFFICE",
            "description": "Fixed income savings certificate issued by India Post to encourage small to medium savings with tax exemption.",
            "key_features": "5-year fixed tenure | Guaranteed interest compounded annually | Can be pledged as collateral for bank loans | Unlimited deposit limit.",
            "min_age": 10,
            "max_age": 100,
            "tax_benefits": "Sec 80C"
        },
        {
            "title": "Kisan Vikas Patra (KVP)",
            "category": "POST_OFFICE",
            "description": "Risk-free savings scheme that doubles your invested capital in a specified duration (~115 months).",
            "key_features": "Capital doubles on maturity | Guaranteed by Government of India | Encashable after lock-in period of 2.5 years | Transferable.",
            "min_age": 18,
            "max_age": 100,
            "tax_benefits": "Guaranteed Sovereign Security"
        },
        {
            "title": "Post Office Monthly Income Scheme (MIS)",
            "category": "POST_OFFICE",
            "description": "Reliable monthly income investment scheme for individuals seeking fixed monthly cash flow.",
            "key_features": "Fixed monthly interest payout | 5-year tenure | Joint account option up to Rs 15 Lakhs limit | Zero market risk.",
            "min_age": 10,
            "max_age": 100,
            "tax_benefits": "Safe Monthly Returns"
        },
        {
            "title": "Post Office Recurring Deposit (RD)",
            "category": "POST_OFFICE",
            "description": "Monthly disciplined investment plan for building substantial capital over 5 years with interest compounding quarterly.",
            "key_features": "Deposit starting from Rs 100 per month | 5-year duration | Loan up to 50% after 1 year | Guaranteed returns.",
            "min_age": 10,
            "max_age": 100,
            "tax_benefits": "Disciplined Savings"
        },
        {
            "title": "Post Office Time Deposit (TD / FD)",
            "category": "POST_OFFICE",
            "description": "Government fixed deposit account with options of 1, 2, 3, or 5-year tenure paying annual interest.",
            "key_features": "Tenures: 1yr, 2yr, 3yr, 5yr | 5-year TD eligible for Tax Rebate under 80C | Interest compounded quarterly, paid annually.",
            "min_age": 10,
            "max_age": 100,
            "tax_benefits": "Sec 80C (5-Yr TD)"
        },
        {
            "title": "Post Office Savings Account",
            "category": "POST_OFFICE",
            "description": "Standard banking savings account backed by India Post with ATM and Internet Banking facilities.",
            "key_features": "Min balance Rs 500 | 4.0% p.a. interest | Tax deduction up to Rs 10,000 under Sec 80TTA | ATM card & cheque book available.",
            "min_age": 10,
            "max_age": 100,
            "tax_benefits": "Sec 80TTA"
        },
        {
            "title": "Mahila Samman Savings Certificate",
            "category": "POST_OFFICE",
            "description": "Special short-term government savings scheme introduced specifically to empower women and girl investors.",
            "key_features": "2-year tenure | High fixed interest rate (~7.5% p.a.) | Partial withdrawal up to 40% after 1 year | Max deposit Rs 2 Lakhs.",
            "min_age": 0,
            "max_age": 100,
            "tax_benefits": "Special Women Benefit"
        }
    ]

    for plan in post_office_plans:
        existing = Product.query.filter_by(title=plan["title"]).first()
        if not existing:
            prod = Product(**plan)
            db.session.add(prod)

    # 7. Seed Sample Financial Blogs
    sample_blogs = [
        {
            "title": "LIC Jeevan Labh vs Post Office PPF: Which is Better for Your Future?",
            "slug": "lic-jeevan-labh-vs-post-office-ppf",
            "content": "When planning your long-term financial security in Rajasthan, choosing between LIC Jeevan Labh (Plan 936) and Post Office Public Provident Fund (PPF) is a common dilemma. Jeevan Labh gives you guaranteed life insurance cover plus handsome bonus payouts, while PPF offers 100% tax-free returns under EEE status. Visit Mukesh Ajmera's office in Sarwar for personalized calculation!",
            "author": "Mukesh Ajmera"
        },
        {
            "title": "Why Sukanya Samriddhi Yojana (SSY) is the Best Gift for Your Daughter",
            "slug": "sukanya-samriddhi-yojana-best-gift-for-daughter",
            "content": "Sukanya Samriddhi Yojana offers an unmatched interest rate of 8.2% p.a. guaranteed by the Government of India. With tax benefits under Section 80C and tax-free maturity payouts at age 21, it secures your daughter's higher education and wedding expenses smoothly.",
            "author": "Mukesh Ajmera"
        }
    ]

    for b in sample_blogs:
        existing = Blog.query.filter_by(slug=b["slug"]).first()
        if not existing:
            blog = Blog(**b)
            db.session.add(blog)

    db.session.commit()
    print("Database seeding completed successfully!")
