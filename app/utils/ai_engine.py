import requests
import json
import urllib.parse
from app.models import AISettings, Product
from app.utils.vector_store import vector_db_instance

def generate_ai_response(user_message, user_phone=None, user_location="Sarwar, Rajasthan", user_name="Guest", current_user_obj=None):
    """
    Generates Human-like Smart Advisory response using Vector DB Semantic Retrieval RAG
    and active AI provider (OpenAI, Gemini, Local LLM, or Vector RAG Engine).
    """
    ai_settings = AISettings.query.first()
    active_provider = ai_settings.active_provider if ai_settings else "vector_rag"
    api_key = ai_settings.api_key if ai_settings else ""
    local_endpoint = ai_settings.local_endpoint if ai_settings else "http://localhost:11434/api/generate"
    
    advisor_name = getattr(ai_settings, 'advisor_name', 'Mukesh Ajmera') or 'Mukesh Ajmera'
    office_address = getattr(ai_settings, 'office_address', 'Near Bhimeshwar Mahadev, Dada Badi, Sarwar 305403, Ajmer, Rajasthan') or 'Near Bhimeshwar Mahadev, Dada Badi, Sarwar 305403, Ajmer, Rajasthan'
    office_phone = getattr(ai_settings, 'office_phone', '+91 98299 43216') or '+91 98299 43216'

    base_system_prompt = ai_settings.system_prompt if (ai_settings and ai_settings.system_prompt) else (
        f"You are LIC MITRA, Human-like Expert Sales & Financial Advisor for {advisor_name} LIC & Post Office Services, Sarwar, Rajasthan."
    )

    # 1. Initialize / Ensure Vector DB Index is built
    products = Product.query.filter_by(is_active=True).all()
    if not vector_db_instance.is_indexed:
        vector_db_instance.build_index(products)

    # 2. Perform Vector Search to retrieve semantic domain context (Vector RAG)
    vector_results = vector_db_instance.search(user_message, top_k=3)
    
    vector_context = ""
    confidence_percent = 95
    matched_plan = None

    if vector_results:
        confidence_percent = vector_results[0]["confidence_percent"]
        context_snippets = []
        for res in vector_results:
            doc = res["document"]
            context_snippets.append(f"[{doc['title']}] {doc['content']}")
            if not matched_plan and doc.get("metadata", {}).get("type") == "product":
                matched_plan = doc["metadata"]["title"]
        vector_context = "\n".join(context_snippets)

    # Secondary intent matching if vector search didn't pick a direct product title
    if not matched_plan:
        msg_lower = user_message.lower()
        for prod in products:
            words = prod.title.lower().split()
            if prod.title.lower() in msg_lower or any(w in msg_lower for w in words if len(w) > 3):
                matched_plan = prod.title
                break

    if not matched_plan:
        msg_lower = user_message.lower()
        if any(kw in msg_lower for kw in ["lic", "policy", "bima", "insurance"]):
            matched_plan = "LIC Policy Guidance"
        elif any(kw in msg_lower for kw in ["post office", "ppf", "ssy", "savings", "dak"]):
            matched_plan = "Post Office Scheme"
        elif any(kw in msg_lower for kw in ["buy", "interest", "kharidna", "invest", "tax"]):
            matched_plan = "Financial Advisory Services"

    # Construct Dynamic WhatsApp Lead Conversion URL with User Name
    whatsapp_url = None
    if matched_plan:
        whatsapp_text = f"Hello {advisor_name} Ji, I am {user_name}. I am interested in {matched_plan}. My Location: {user_location}"
        encoded_text = urllib.parse.quote(whatsapp_text)
        whatsapp_url = f"https://wa.me/919829943216?text={encoded_text}"

    # Build Vector Augmented System Prompt
    system_prompt = (
        f"{base_system_prompt}\n\n"
        f"[RETRIEVED VECTOR KNOWLEDGE BASE CONTEXT]:\n{vector_context}\n\n"
        f"[OFFICE LOCATION & ADVISOR]: {advisor_name}, {office_address}, Phone: {office_phone}\n"
        f"[USER PROFILE]: Name: {user_name}, Phone: {user_phone or 'Guest'}, Location: {user_location}.\n"
        "Instructions: Respond like a high-converting, persuasive, friendly sales & financial advisor. "
        "Engage in natural conversation, quote tax benefits (Sec 80C, 10(10D)), and guide the user to choose the best scheme."
    )

    response_text = ""

    # 3. Call Active AI Engine Provider (If Vector RAG mode or API key missing, run Vector DB Sales Engine directly!)
    if active_provider == "vector_rag" or not api_key:
        response_text = generate_human_vector_fallback(user_message, products, matched_plan, vector_results, user_location, advisor_name, office_address, office_phone, user_name)
    else:
        try:
            if active_provider == "local" and local_endpoint:
                payload = {
                    "model": "llama3",
                    "prompt": f"{system_prompt}\n\nUser Query: {user_message}\nAdvisor Answer:",
                    "stream": False
                }
                res = requests.post(local_endpoint, json=payload, timeout=3)
                if res.status_code == 200:
                    data = res.json()
                    response_text = data.get("response", "").strip()

            elif active_provider == "openai" and api_key:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.7
                }
                res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    response_text = data['choices'][0]['message']['content'].strip()

            elif active_provider == "gemini" and api_key:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                payload = {
                    "contents": [
                        {"parts": [{"text": f"{system_prompt}\n\nUser: {user_message}"}]}
                    ]
                }
                res = requests.post(url, json=payload, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    response_text = data['candidates'][0]['content']['parts'][0]['text'].strip()

        except Exception as e:
            print(f"Provider ({active_provider}) offline: {e}")

    # Fallback to Sales Vector DB Engine if response empty
    if not response_text:
        response_text = generate_human_vector_fallback(user_message, products, matched_plan, vector_results, user_location, advisor_name, office_address, office_phone, user_name)

    return {
        "response": response_text,
        "matched_plan": matched_plan,
        "confidence_score": f"{confidence_percent}%",
        "whatsapp_url": whatsapp_url,
        "provider_used": active_provider
    }


def generate_human_vector_fallback(user_message, products, matched_plan, vector_results, user_location, advisor_name="Mukesh Ajmera", office_address="Sarwar", office_phone="+91 98299 43216", user_name="Guest", current_user_obj=None):
    """
    Human-like expert sales & financial advisor conversational engine tuned for Mukesh Ajmera Sarwar.
    Provides natural multi-turn interactive discussions in Hindi, English, and Hinglish.
    """
    msg = user_message.lower().strip()

    # 1. User Profile Details Inquiry (Logged In vs Guest)
    if any(k in msg for k in ["profile", "my profile", "my details", "meri profile", "mera profile", "my info", "mera vivaran"]):
        if current_user_obj:
            dob_val = getattr(current_user_obj, 'dob', None) or 'Not Set'
            email_val = getattr(current_user_obj, 'email', None) or 'Not Set'
            lat_val = getattr(current_user_obj, 'latitude', None) or 26.0618
            lng_val = getattr(current_user_obj, 'longitude', None) or 75.0183
            phone_val = getattr(current_user_obj, 'phone', None) or 'N/A'
            name_val = getattr(current_user_obj, 'name', None) or user_name

            return (
                f"👤 **आपकी पंजीकृत ग्राहक प्रोफ़ाइल (Customer Profile Details):**\n\n"
                f"• **पूरा नाम (Full Name):** {name_val}\n"
                f"• **पंजीकृत मोबाइल:** +91 {phone_val}\n"
                f"• **ईमेल पता (Email):** {email_val}\n"
                f"• **जन्म तिथि (DOB):** {dob_val}\n"
                f"• **स्थान (Saved Location):** {user_location}\n"
                f"• **मानचित्र अक्षांश/रेखांश (Lat, Long):** {lat_val}, {lng_val}\n\n"
                f"✏️ स्थान या नाम अपडेट करने हेतु प्रोफ़ाइल सहेजें।"
            )
        else:
            return (
                "🔒 **आप सम्प्रति अतिथि (Guest) के रूप में चैट कर रहे हैं।**\n\n"
                "अपनी व्यक्तिगत प्रोफ़ाइल देखने एवं स्थान सहेजने हेतु कृपया एडमिन / ग्राहक पोर्टल में लॉगिन करें।\n\n"
                "🔑 **लॉगिन लिंक:** `http://localhost:5050/login`"
            )

    # 2. Warm Human Greetings & Openers (Catches "good morning", "good evening", "hi", "hello", etc.)
    greetings = ["hello", "hi", "hey", "namaste", "namaskar", "ram ram", "khamma ghani", "kem cho", "good morning", "good evening", "good afternoon", "gud morning", "gud evening", "kaise ho", "kaise h", "su prabhat", "subah"]
    if any(k in msg for k in greetings):
        greeting_word = "Good Morning!" if "morning" in msg else ("Good Evening!" if "evening" in msg else "Namaste! Khamma Ghani!")
        return (
            f"🙏 **{greeting_word}**\n\n"
            f"Hello **{user_name}**! मैं **LIC MITRA ({advisor_name} सरवाड़)** — आपका समर्पित वित्तीय एवं बीमा सलाहकार हूँ।\n"
            f"आपके क्षेत्र (**{user_location}**) के परिवारों के लिए हम एलआईसी और डाकघर की सर्वश्रेष्ठ बचत योजनाओं की सलाह प्रदान करते हैं।\n\n"
            "💬 **आप मुझसे अपनी आवश्यकतानुसार चर्चा कर सकते हैं:**\n"
            "1️⃣ **मासिक बचत:** *'₹1,000 या ₹2,000 प्रति माह कहां निवेश करें?'*\n"
            "2️⃣ **लोकप्रिय योजनाएं:** *'LIC Jeevan Labh (Plan 936) या Post Office PPF के क्या फायदे हैं?'*\n"
            "3️⃣ **बेटियों का भविष्य:** *'Sukanya Samriddhi Scheme (SSY 8.2%) क्या है?'*\n"
            "4️⃣ **प्रोफ़ाइल विवरण:** *'My Profile Details'*\n"
            "5️⃣ **टैक्स बचत (80C):** *'₹1.5 लाख टैक्स कैसे बचाएं?'*\n\n"
            "बताइए, आज मैं आपके परिवार की किस बचत योजना में मार्गदर्शन कर सकता हूँ?"
        )

    # 2. About Mukesh Ajmera / Sarwar Office Profile Inquiries
    if any(k in msg for k in ["mukesh", "ajmera", "who are you", "office", "address", "pata", "sarwar", "contact", "phone", "kahan"]):
        return (
            f"👤 **{advisor_name} — वरिष्ठ वित्तीय एवं बीमा सलाहकार:**\n\n"
            "• **अनुभव:** 20+ वर्षों का विश्वसनीय वित्तीय परामर्श अनुभव सरवाड़ एवं अजमेर क्षेत्र में।\n"
            "• **विशेषज्ञता:** भारतीय जीवन बीमा निगम (LIC) बीमा पॉलिसी एवं भारतीय डाक (Post Office) संप्रभु बचत योजनाएं।\n"
            f"📍 **कार्यालय पता:** {office_address}\n"
            f"📞 **फोन / WhatsApp:** {office_phone}\n\n"
            "क्या आप कार्यालय आने हेतु समय तय करना चाहते हैं या किसी योजना का कैलकुलेशन पाना चाहते हैं?"
        )

    # 3. Monthly Budget & Investment Calculation Inquiries
    if any(k in msg for k in ["per month", "mahina", "prati mah", "budget", "invest", "kama", "bachat", "kitna jama", "monthly", "1000", "2000", "3000", "5000"]):
        return (
            "💰 **मासिक बचत एवं रिटर्न गाइड (Monthly Investment Plan):**\n\n"
            "1️⃣ **₹1,000 से ₹2,000 प्रति माह:**\n"
            "• **LIC Jeevan Labh (Plan 936):** सीमित अवधि प्रीमियम (16 वर्ष जमा, 25 वर्ष पर मेच्योरिटी)। अनुमानित टैक्स-फ्री रिटर्न ₹10-12 लाख + जीवन बीमा सुरक्षा!\n"
            "• **Post Office PPF:** 15 वर्ष की संप्रभु गारंटी योजना। 7.1% चक्रवृद्धि ब्याज + 100% EEE टैक्स फ्री।\n\n"
            "2️⃣ **₹3,000 से ₹5,000 प्रति माह:**\n"
            "• **LIC Jeevan Umang:** प्रीमियम भुगतान के बाद आजीवन 8% वार्षिक गारंटीड रिटर्न + मेच्योरिटी।\n"
            "• **Sukanya Samriddhi (SSY):** बेटियों हेतु 8.2% उच्चतम ब्याज।\n\n"
            "💡 अपनी सटीक आयु दर्ज करें, मैं आपके लिए सबसे उपयुक्त तालिका (Illustration) तैयार करूँगा!"
        )

    # 4. Daughter / Girl Child Savings (Sukanya / Kanyadaan)
    if any(k in msg for k in ["beti", "daughter", "girl", "sukanya", "ssy", "shadi", "kanya"]):
        return (
            "👧 **बेटियों के सुरक्षित भविष्य की सर्वोत्तम योजनाएं:**\n\n"
            "1️⃣ **Sukanya Samriddhi Yojana (Post Office SSY):**\n"
            "• **ब्याज दर:** 8.2% (डाकघर की उच्चतम ब्याज दर)।\n"
            "• **पात्रता:** 10 वर्ष तक की बालिका हेतु। धारा 80C में छूट एवं 21 वर्ष में पूर्णतः टैक्स-फ्री मेच्योरिटी।\n\n"
            "2️⃣ **LIC कन्यादान / Jeevan Labh:**\n"
            "• **विशेषता:** पिता के साथ दुर्घटना या अप्रत्याशित घटना की स्थिति में आगे के सभी प्रीमियम माफ + बालिका को तत्काल आर्थिक सहायता एवं मेच्योरिटी पर पूरी राशि!\n\n"
            "अपनी बेटी की वर्तमान आयु बताएं, ताकि हम सटीक गणना कर सकें।"
        )

    # 5. Tax Savings (Sec 80C & Sec 10(10D))
    if any(k in msg for k in ["tax", "80c", "10(10d)", "kar", "tax bachat", "tax saving"]):
        return (
            "🛡️ **आयकर धारा 80C एवं 10(10D) में टैक्स बचत एडवाइस:**\n\n"
            "• **धारा 80C (Section 80C):** LIC प्रीमियम एवं Post Office PPF/SSY में वार्षिक ₹1,50,000 तक जमा पर पूरी टैक्स छूट।\n"
            "• **धारा 10(10D):** LIC पॉलिसी की मेच्योरिटी एवं डेथ क्लेम की पूरी राशि **100% टैक्स फ्री** होती है।\n"
            "• **EEE स्टेटस (PPF & SSY):** जमा, ब्याज एवं मेच्योरिटी तीनों स्तरों पर शून्य टैक्स!\n\n"
            "क्या आप इस वित्तीय वर्ष हेतु अपना टैक्स बचाना चाहते हैं?"
        )

    # 6. Comparison Guide (LIC vs Post Office)
    if any(k in msg for k in ["compare", "vs", "difference", "tulna", "kis me invest", "which is better"]):
        return (
            "📊 **LIC बनाम पोस्ट ऑफिस (सच्चा तुलनात्मक मार्गदर्शन):**\n\n"
            "1️⃣ **भारतीय जीवन बीमा निगम (LIC):**\n"
            "• **मुख्य लाभ:** परिवार की आर्थिक सुरक्षा हेतु जीवन बीमा (Life Risk Cover) + वार्षिक बोनस + 100% टैक्स फ्री मेच्योरिटी।\n"
            "• **सर्वश्रेष्ठ:** Jeevan Labh (936), Jeevan Umang (945).\n\n"
            "2️⃣ **भारतीय डाकघर (Post Office):**\n"
            "• **मुख्य लाभ:** 100% भारत सरकार की गारंटी (Sovereign Security) + उच्चतम निश्चित ब्याज (8.2% तक)।\n"
            "• **सर्वश्रेष्ठ:** PPF (7.1%), SSY (8.2%), Senior Citizen Scheme (8.2%).\n\n"
            "💡 **मुकेश अजमेरा की सलाह:** जीवन बीमा सुरक्षा हेतु LIC एवं लिक्विड बचत हेतु Post Office का 50-50% संतुलन बनाएं!"
        )

    # 7. Pension & Retirement Inquiries
    if any(k in msg for k in ["pension", "retirement", "monthly income", "senior", "scss", "mis"]):
        return (
            "👴 **वरिष्ठ नागरिकों एवं पेंशनधारियों हेतु नियमित आय योजनाएं:**\n\n"
            "• **Post Office SCSS (Senior Citizen Savings Scheme):** 8.2% त्रैमासिक ब्याज भुगतान (60 वर्ष से अधिक आयु हेतु)।\n"
            "• **Post Office MIS (Monthly Income Scheme):** हर महीने निश्चित ब्याज सीधे आपके बैंक खाते में।\n"
            "• **LIC Jeevan Umang:** प्रीमियम भुगतान के बाद आजीवन 8% गारंटीड पेंशन हर साल!\n\n"
            "क्या आप मासिक आय योजना या एकमुश्त जमा पेंशन के बारे में विस्तृत विवरण चाहते हैं?"
        )

    # 8. All 20 Plans List Inquiries (10 LIC + 10 Post Office Real Data)
    if any(k in msg for k in ["all plan", "all 20", "20 plan", "sabhi yojana", "list", "options", "schemes"]):
        return (
            "📋 **मुकेश अजमेरा अधिकृत सभी 20 मुख्य योजनाएं (20 Official Schemes):**\n\n"
            "🛡️ **10 प्रमुख एलआईसी बीमा योजनाएं (LIC Plans):**\n"
            "1. **LIC Jeevan Labh (Plan 936):** सीमित प्रीमियम pay (16 yrs pay for 25 yrs maturity) + हाई बोनस + 10(10D) टैक्स फ्री।\n"
            "2. **LIC Jeevan Umang (Plan 945):** 100 वर्ष लाइफ कवर + PPT के बाद आजीवन 8% गारंटीड सालाना रिटर्न।\n"
            "3. **LIC Tech Term (Plan 854):** कम प्रीमियम में बड़ा लाइफ रिस्क कवर + नॉन-स्मोकर डिस्काउंट।\n"
            "4. **LIC Jeevan Anand (Plan 915):** मेच्योरिटी पर एकमुश्त राशि + मेच्योरिटी के बाद भी आजीवन लाइफ कवर जारी।\n"
            "5. **LIC Nivesh Plus (Plan 849):** सिंगल प्रीमियम ULIP + 4 फंड विकल्प + मार्केट ग्रोथ।\n"
            "6. **LIC SIIP (Plan 852):** रेगुलर प्रीमियम ULIP + गारंटीड एडिशन्स + 5 साल बाद आंशिक निकासी।\n"
            "7. **LIC Cancer Cover (Plan 905):** कैंसर हेल्थ कवर + अर्ली स्टेज पर प्रीमियम वेवर + मंथली इनकम।\n"
            "8. **LIC Bachat Plus (Plan 861):** सिंगल / लिमिटेड प्रीमियम बचत + गारंटीड टर्मिनल एडिशन्स।\n"
            "9. **LIC Jeevan Shiromani (Plan 847):** HNI प्लान (न्यूनतम ₹1 करोड़ Sum Assured) + क्रिटिकल इलनेस कवर।\n"
            "10. **LIC Dhan Sanchay (Plan 865):** गारंटीड रेगुलर इनकम स्ट्रीम भुगतान।\n\n"
            "📮 **10 प्रमुख डाकघर बचत योजनाएं (India Post Schemes):**\n"
            "1. **Public Provident Fund (PPF):** 15 वर्ष tenure @ 7.1% चक्रवृद्धि ब्याज + 100% EEE टैक्स फ्री।\n"
            "2. **Sukanya Samriddhi Yojana (SSY):** बेटियों हेतु 8.2% उच्चतम ब्याज (10 वर्ष तक की बालिका)।\n"
            "3. **Senior Citizen Scheme (SCSS):** 60+ वरिष्ठ नागरिकों हेतु 8.2% त्रैमासिक ब्याज भुगतान।\n"
            "4. **National Savings Certificate (NSC):** 5 वर्ष निश्चित रिटर्न + धारा 80C टैक्स छूट।\n"
            "5. **Kisan Vikas Patra (KVP):** 115 महीने में धन 100% भारत सरकार गारंटी से दोगुना।\n"
            "6. **Post Office MIS (Monthly Income):** हर महीने निश्चित ब्याज सीधे आपके बैंक खाते में।\n"
            "7. **Post Office Recurring Deposit (RD):** ₹100/माह से 5 वर्ष अनुशासित बचत।\n"
            "8. **Post Office Time Deposit (TD/FD):** 1, 2, 3, 5 वर्ष एफडी (5 वर्ष पर 80C छूट)।\n"
            "9. **Mahila Samman Savings Certificate:** महिलाओं हेतु 2 वर्ष @ 7.5% ब्याज।\n"
            "10. **Post Office Savings Account:** 4.0% ब्याज + धारा 80TTA ₹10,000 तक टैक्स छूट।\n\n"
            "💡 **मुकेश अजमेरा सलाह:** किसी भी योजना की आयु अनुसार कोटेशन देखने हेतु योजना का नाम दर्ज करें!"
        )

    # 9. Vector Database Semantic Match Utilization
    if vector_results:
        top_match = vector_results[0]["document"]
        if top_match.get("metadata", {}).get("type") == "product":
            prod = next((p for p in products if p.title == top_match["title"]), None)
            if prod:
                return (
                    f"🌟 **{prod.title} (विशेषज्ञ विश्लेषण):**\n\n"
                    f"📝 **योजना विवरण:** {prod.description}\n"
                    f"✨ **मुख्य आकर्षण:** {prod.key_features}\n"
                    f"👤 **पात्रता आयु:** {prod.min_age} वर्ष से {prod.max_age} वर्ष तक\n"
                    f"🛡️ **टैक्स लाभ:** {prod.tax_benefits} (100% टैक्स फ्री मेच्योरिटी)\n\n"
                    f"क्या आप अपनी आयु के अनुसार {prod.title} का मेच्योरिटी कैलकुलेशन देखना चाहते हैं?"
                )

    # 10. Secondary Intent Product Match
    if matched_plan:
        prod = next((p for p in products if p.title == matched_plan), None)
        if prod:
            return (
                f"🤝 **{prod.title} योजना की जानकारी:**\n\n"
                f"📝 **विवरण:** {prod.description}\n"
                f"✨ **विशेषताएं:** {prod.key_features}\n"
                f"👤 **पात्रता:** {prod.min_age} से {prod.max_age} वर्ष\n"
                f"🛡️ **टैक्स नियम:** {prod.tax_benefits}\n\n"
                f"क्या आप {prod.title} की प्रीमियम कोटेशन या व्यक्तिगत जानकारी पाना चाहते हैं?"
            )

    # 11. Interactive Conversational Fallback (Never a static contact dump!)
    return (
        "💡 **मैं समझ सकता हूँ!**\n\n"
        "एलआईसी बीमा (LIC Policy) और डाकघर (Post Office) की कई योजनाएं उपलब्ध हैं। आपके परिवार की आवश्यकता के अनुसार सही चुनाव में मदद करने के लिए कृपया बताएं:\n\n"
        "1. आपकी अनुमानित आयु क्या है?\n"
        "2. आप कितना बचत करना चाहते हैं (उदा. ₹1,000 या ₹3,000 प्रति माह)?\n"
        "3. मुख्य लक्ष्य: बेटियों की शिक्षा, स्वयं की पेंशन, या टैक्स बचत (Sec 80C)?\n\n"
        "अपनी आवश्यकता दर्ज करें, मैं तुरंत आपके लिए सर्वोत्तम योजना का सुझाव दूंगा!"
    )



