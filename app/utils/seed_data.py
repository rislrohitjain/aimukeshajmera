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
        {"url_path": "/about-mukesh-ajmera", "priority": "0.9"},
        {"url_path": "/lic-services-sarwar", "priority": "0.9"},
        {"url_path": "/post-office-schemes", "priority": "0.9"},
        {"url_path": "/contact", "priority": "0.8"},
        {"url_path": "/blogs", "priority": "0.8"}
    ]
    for sm in default_sitemaps:
        if not SitemapUrl.query.filter_by(url_path=sm["url_path"]).first():
            db.session.add(SitemapUrl(**sm))

    # Remove any existing /checkdb or /login sitemap url entries
    for unwanted_path in ["/checkdb", "/login"]:
        old_sm = SitemapUrl.query.filter_by(url_path=unwanted_path).first()
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

    # 5. Seed LIC Products (Latest & Popular Plans)
    lic_plans = [
        {
            "title": "LIC Jeevan Utsav (Plan 871)",
            "category": "LIC",
            "description": "Latest non-linked, non-participating whole life insurance plan offering guaranteed lifetime income of 10% of Basic Sum Assured every year after premium paying term.",
            "key_features": "Guaranteed 10% annual income for life | Limited PPT (5 to 16 years) | Flexi Income option earning 5.5% interest | Guaranteed additions of ₹40/thousand during PPT.",
            "min_age": 0,
            "max_age": 65,
            "tax_benefits": "Sec 80C & Sec 10(10D)"
        },
        {
            "title": "LIC Amritbaal (Plan 874)",
            "category": "LIC",
            "description": "Latest individual life insurance savings plan specially designed for children's higher education and future financial milestones with highest guaranteed additions.",
            "key_features": "Highest Guaranteed Additions of ₹80 per thousand BSA every year | Entry age 30 days to 13 years | Flexible single or limited premium | Premium Waiver Rider available.",
            "min_age": 0,
            "max_age": 13,
            "tax_benefits": "Sec 80C & Sec 10(10D)"
        },
        {
            "title": "LIC Jeevan Labh (Plan 936)",
            "category": "LIC",
            "description": "High-demand limited premium paying, with-profits endowment plan offering exceptional bonuses and safe long-term wealth accumulation.",
            "key_features": "Pay for limited term (e.g. 10 pay 16 term, 15 pay 21 term, 16 pay 25 term) | Highest bonus rate | Loan available after 2 years | High maturity returns.",
            "min_age": 8,
            "max_age": 59,
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
            "title": "LIC Tech Term (Plan 854)",
            "category": "LIC",
            "description": "Pure non-participating online term assurance policy offering substantial financial protection to the family at very affordable premium rates.",
            "key_features": "High Sum Assured discounts | Level or Increasing Sum Assured options | Low premium rates for non-smokers | Tax benefits under Sec 80C.",
            "min_age": 18,
            "max_age": 65,
            "tax_benefits": "Sec 80C & Sec 10(10D)"
        },
        {
            "title": "LIC New Jeevan Anand (Plan 915)",
            "category": "LIC",
            "description": "Double benefit plan combining financial protection against death throughout life with lump sum payout at the end of selected term.",
            "key_features": "Lump sum maturity payout | Continued life cover even after maturity | Accident benefit rider | Annual bonus addition.",
            "min_age": 18,
            "max_age": 50,
            "tax_benefits": "Sec 80C & Sec 10(10D)"
        },
        {
            "title": "LIC Saral Pension (Plan 862)",
            "category": "LIC",
            "description": "Standard single premium immediate annuity plan offering lifelong guaranteed pension with 100% Return of Purchase Price (ROP) to nominees.",
            "key_features": "Guaranteed lifelong regular pension | 100% purchase price return to nominee | Single life or Joint life annuity options | Loan available after 6 months.",
            "min_age": 40,
            "max_age": 80,
            "tax_benefits": "Sec 80C"
        },
        {
            "title": "LIC Bima Jyoti (Plan 860)",
            "category": "LIC",
            "description": "Non-linked, non-participating limited premium endowment plan providing guaranteed additions throughout policy term.",
            "key_features": "Guaranteed additions of ₹50 per thousand BSA at end of each policy year | 5 years shorter PPT than policy term | Loan facility | High demand savings plan.",
            "min_age": 0,
            "max_age": 60,
            "tax_benefits": "Sec 80C & Sec 10(10D)"
        },
        {
            "title": "LIC Index Plus (Plan 873)",
            "category": "LIC",
            "description": "Latest unit-linked life insurance product investing in benchmark indices (Nifty 50 and Nifty Auto) with life risk cover.",
            "key_features": "Choice of 2 index funds | Guaranteed additions as % of annual premium | Partial withdrawals after 5 years | Flexible PPT.",
            "min_age": 0,
            "max_age": 60,
            "tax_benefits": "Sec 80C & Sec 10(10D)"
        },
        {
            "title": "LIC Jeevan Shanti (Plan 858)",
            "category": "LIC",
            "description": "Single premium deferred annuity plan allowing you to lock in guaranteed pension rates today for your future retirement.",
            "key_features": "Guaranteed annuity rates fixed at inception | Deferment period from 1 to 12 years | Joint life deferred annuity option | Death benefit payout.",
            "min_age": 30,
            "max_age": 79,
            "tax_benefits": "Sec 80C"
        },
        {
            "title": "LIC Dhan Sanchay (Plan 865)",
            "category": "LIC",
            "description": "Non-linked, non-participating, individual life insurance savings plan providing guaranteed income stream during payout period.",
            "key_features": "Guaranteed income payout after PPT | Enhanced benefits for higher premiums | Death benefit payable as lump sum or installments.",
            "min_age": 3,
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
            "title": "LIC SIIP (Plan 852)",
            "category": "LIC",
            "description": "Unit-Linked Regular Premium plan combining insurance protection and investment with guaranteed additions over policy period.",
            "key_features": "Regular premium ULIP | Guaranteed additions added to unit fund | Partial withdrawal allowed after 5 years | Flexible fund selection.",
            "min_age": 0,
            "max_age": 65,
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
            "title": "LIC Jeevan Shiromani (Plan 847)",
            "category": "LIC",
            "description": "High net-worth individual (HNI) plan providing high life cover and financial support for critical illnesses.",
            "key_features": "Minimum Sum Assured Rs. 1 Crore | Built-in Critical Illness cover | Guaranteed Additions @ Rs. 50 per thousand BSA | Limited PPT.",
            "min_age": 18,
            "max_age": 55,
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
        }
    ]

    for plan in lic_plans:
        existing = Product.query.filter_by(title=plan["title"]).first()
        if not existing:
            prod = Product(**plan)
            db.session.add(prod)
        else:
            existing.description = plan["description"]
            existing.key_features = plan["key_features"]
            existing.tax_benefits = plan["tax_benefits"]
            existing.min_age = plan["min_age"]
            existing.max_age = plan["max_age"]

    # 6. Seed Post Office Plans (Latest Schemes & Updated Benefits)
    post_office_plans = [
        {
            "title": "Sukanya Samriddhi Yojana (SSY)",
            "category": "POST_OFFICE",
            "description": "Government-backed savings scheme for girl children offering the highest interest rate of 8.2% p.a. with complete triple tax exemption (EEE).",
            "key_features": "Highest interest rate (8.2% p.a.) | Exclusively for girl child up to 10 years | Deposit ₹250 to ₹1.5 Lakh/yr | Full EEE tax exemption | Matures at age 21.",
            "min_age": 0,
            "max_age": 10,
            "tax_benefits": "Sec 80C (EEE Status - 100% Tax Free)"
        },
        {
            "title": "Senior Citizen Savings Scheme (SCSS)",
            "category": "POST_OFFICE",
            "description": "Safe government savings scheme specially for senior citizens aged 60+ offering guaranteed 8.2% quarterly interest with doubled ₹30 Lakh deposit ceiling.",
            "key_features": "Enhanced maximum limit ₹30 Lakh | High 8.2% p.a. quarterly interest credited directly to account | 5-year tenure extendable by 3 years | 100% sovereign guarantee.",
            "min_age": 60,
            "max_age": 100,
            "tax_benefits": "Sec 80C"
        },
        {
            "title": "Public Provident Fund (PPF)",
            "category": "POST_OFFICE",
            "description": "Sovereign guaranteed 15-year wealth builder offering 7.1% interest compounded annually and triple tax exemption (EEE).",
            "key_features": "15-year tenure extendable in 5-year blocks | EEE tax exemption | Loan against PPF from 3rd year | Partial withdrawal from 7th year.",
            "min_age": 0,
            "max_age": 100,
            "tax_benefits": "Sec 80C (Exempt-Exempt-Exempt)"
        },
        {
            "title": "Post Office Monthly Income Scheme (MIS)",
            "category": "POST_OFFICE",
            "description": "Guaranteed regular monthly income scheme with enhanced deposit limits of ₹9 Lakh for single accounts and ₹15 Lakh for joint accounts at 7.4% p.a.",
            "key_features": "7.4% p.a. monthly interest payout | Single limit ₹9 Lakh, Joint limit ₹15 Lakh | 5-year tenure | Capital 100% safe with government backing.",
            "min_age": 10,
            "max_age": 100,
            "tax_benefits": "Guaranteed Monthly Cashflow"
        },
        {
            "title": "Mahila Samman Savings Certificate (MSSC)",
            "category": "POST_OFFICE",
            "description": "Special government small savings scheme introduced exclusively for women and girl investors offering high fixed 7.5% quarterly compounded return.",
            "key_features": "7.5% p.a. fixed interest | 2-year short tenure | Deposit up to ₹2 Lakh | Partial withdrawal up to 40% after 1 year | Safe sovereign guarantee.",
            "min_age": 0,
            "max_age": 100,
            "tax_benefits": "Special Women Savings Scheme"
        },
        {
            "title": "National Savings Certificate (NSC)",
            "category": "POST_OFFICE",
            "description": "5-year fixed return government savings certificate offering 7.7% compounded interest and Section 80C tax deduction.",
            "key_features": "7.7% p.a. compounded annually, paid at maturity | Section 80C deduction on investment & accrued interest | Collateral security for bank loans.",
            "min_age": 10,
            "max_age": 100,
            "tax_benefits": "Sec 80C"
        },
        {
            "title": "Kisan Vikas Patra (KVP)",
            "category": "POST_OFFICE",
            "description": "Risk-free sovereign savings scheme doubling your invested capital in 115 months (9 years & 7 months) at 7.5% p.a.",
            "key_features": "Capital doubles on maturity (115 months) | 7.5% compounded annually | Premature encashment after 2.5 years | Fully transferable.",
            "min_age": 18,
            "max_age": 100,
            "tax_benefits": "Guaranteed Sovereign Security"
        },
        {
            "title": "Post Office Time Deposit (5-Year TD / FD)",
            "category": "POST_OFFICE",
            "description": "Government fixed term deposit offering 7.5% interest compounded quarterly, paid annually, with Section 80C tax deduction.",
            "key_features": "7.5% p.a. quarterly compounded interest | 5-year tenure eligible under Section 80C | Guaranteed government return | Loan against deposit.",
            "min_age": 10,
            "max_age": 100,
            "tax_benefits": "Sec 80C (5-Yr TD)"
        },
        {
            "title": "Post Office Recurring Deposit (RD)",
            "category": "POST_OFFICE",
            "description": "Monthly disciplined investment plan for building substantial capital over 5 years with 6.7% interest compounding quarterly.",
            "key_features": "Deposit starting from Rs 100 per month | 6.7% quarterly compounded | 5-year duration | Loan up to 50% after 1 year | Guaranteed returns.",
            "min_age": 10,
            "max_age": 100,
            "tax_benefits": "Disciplined Savings"
        },
        {
            "title": "Post Office Savings Account",
            "category": "POST_OFFICE",
            "description": "Standard banking savings account backed by India Post with 4.0% interest, ATM and Internet Banking facilities.",
            "key_features": "Min balance Rs 500 | 4.0% p.a. interest | Tax deduction up to Rs 10,000 under Sec 80TTA | ATM card & cheque book available.",
            "min_age": 10,
            "max_age": 100,
            "tax_benefits": "Sec 80TTA (Up to ₹10k)"
        },
        {
            "title": "Post Office Time Deposit (1, 2, 3-Year TD)",
            "category": "POST_OFFICE",
            "description": "Short to medium term government fixed deposits paying 6.9% to 7.1% interest compounded quarterly and paid annually.",
            "key_features": "1-Year TD: 6.9% | 2-Year TD: 7.0% | 3-Year TD: 7.1% | Zero market risk | Flexible reinvestment on maturity.",
            "min_age": 10,
            "max_age": 100,
            "tax_benefits": "Safe Term Returns"
        }
    ]

    for plan in post_office_plans:
        existing = Product.query.filter_by(title=plan["title"]).first()
        if not existing:
            prod = Product(**plan)
            db.session.add(prod)
        else:
            existing.description = plan["description"]
            existing.key_features = plan["key_features"]
            existing.tax_benefits = plan["tax_benefits"]
            existing.min_age = plan["min_age"]
            existing.max_age = plan["max_age"]

    # 7. Seed Sample Financial Blogs
    sample_blogs = [
        {
            "title": "Latest Post Office Interest Rates & New LIC Plans (2026 Updated Guide)",
            "slug": "latest-post-office-interest-rates-lic-plans-2026",
            "content": "Discover the latest 2026 benefits: Senior Citizen Savings Scheme limit is now ₹30 Lakh at 8.2% interest. Post Office MIS limit has increased to ₹9 Lakh (Single) and ₹15 Lakh (Joint) at 7.4% monthly interest. Sukanya Samriddhi Yojana offers 8.2% with triple tax exemption, while Mahila Samman Certificate offers 7.5% for women. On the LIC side, newly launched LIC Jeevan Utsav (Plan 871) offers 10% guaranteed lifelong income, and LIC Amritbaal (Plan 874) provides highest guaranteed additions of ₹80/thousand for children. Contact Mukesh Ajmera in Sarwar for personalized guidance!",
            "author": "Mukesh Ajmera"
        },
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
        else:
            existing.content = b["content"]
            existing.title = b["title"]

    db.session.commit()
    print("Database seeding completed successfully!")
