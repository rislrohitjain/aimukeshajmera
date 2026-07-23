import re
import math
from collections import Counter

class SimpleVectorDB:
    """
    In-Memory High-Performance Vector Database System for LIC & Post Office Knowledge Base.
    Uses Term Frequency-Inverse Document Frequency (TF-IDF) & Cosine Similarity Vector Embeddings.
    """
    def __init__(self):
        self.documents = []
        self.doc_vectors = []
        self.vocabulary = set()
        self.idf = {}
        self.is_indexed = False

    def _tokenize(self, text):
        """Clean and tokenize text into vector dimensions."""
        if not text:
            return []
        text = text.lower()
        # Extract alphanumeric words (Hindi & English)
        words = re.findall(r'\w+', text, re.UNICODE)
        return [w for w in words if len(w) > 1]

    def build_index(self, product_list=None):
        """Build vector embeddings for all financial schemes and advisory knowledge."""
        self.documents = []
        self.vocabulary = set()

        # 1. Add Knowledge Documents from Pre-loaded Products
        if product_list:
            for prod in product_list:
                doc_text = f"Title: {prod.title}. Category: {prod.category}. Description: {prod.description}. Features: {prod.key_features}. Age: {prod.min_age} to {prod.max_age} years. Tax Benefits: {prod.tax_benefits}."
                self.documents.append({
                    "id": f"prod_{prod.id}",
                    "title": prod.title,
                    "category": prod.category,
                    "content": doc_text,
                    "metadata": {
                        "type": "product",
                        "title": prod.title,
                        "min_age": prod.min_age,
                        "max_age": prod.max_age,
                        "tax_benefits": prod.tax_benefits
                    }
                })

        # 2. Add Curated Expert Knowledge Base (Rules, Tax, Sarwar Office, LIC vs Post Office)
        knowledge_chunks = [
            {
                "id": "kb_sarwar_office",
                "title": "Mukesh Ajmera Sarwar Office & Contact",
                "content": "Mukesh Ajmera Senior LIC Agent and Post Office Financial Advisor in Sarwar Rajasthan. Address: Near Bhimeshwar Mahadev, Dada Badi, Sarwar 305403, Ajmer, Rajasthan. Phone WhatsApp: +91 98299 43216. Sovereign government guarantee 100 percent safety.",
                "metadata": {"type": "contact"}
            },
            {
                "id": "kb_lic_jeevan_labh",
                "title": "LIC Jeevan Labh (Plan 936)",
                "content": "LIC Jeevan Labh Plan 936 is a non-linked participating endowment plan offering high bonus maturity tax free under 10(10D) and premium deduction under Sec 80C. Limited premium paying term (e.g., pay 16 years get maturity at 25 years). Age limit 8 to 59 years.",
                "metadata": {"type": "scheme_detail"}
            },
            {
                "id": "kb_lic_jeevan_umang",
                "title": "LIC Jeevan Umang (Plan 945)",
                "content": "LIC Jeevan Umang Plan 945 is a 100 year whole life assurance plan with 8% guaranteed annual survival benefit payouts for life after premium paying term plus tax free sum assured lump sum maturity.",
                "metadata": {"type": "scheme_detail"}
            },
            {
                "id": "kb_post_office_ppf",
                "title": "Post Office Public Provident Fund (PPF)",
                "content": "Post Office Public Provident Fund PPF scheme 15 year tenure interest rate 7.1 percent per annum compounded annually. Triple Tax Free EEE Status: Deposit, interest, and withdrawal are 100 percent tax free under Sec 80C.",
                "metadata": {"type": "scheme_detail"}
            },
            {
                "id": "kb_post_office_ssy",
                "title": "Sukanya Samriddhi Yojana (SSY)",
                "content": "Sukanya Samriddhi Yojana SSY for girl child up to 10 years age. High interest rate 8.2 percent tax free under 80C. Highest returning post office government savings scheme for girl child higher education and marriage.",
                "metadata": {"type": "scheme_detail"}
            },
            {
                "id": "kb_tax_savings_80c",
                "title": "Tax Savings Sec 80C & 10(10D)",
                "content": "Tax savings guide: Premium up to 1.5 Lakh rupees per year exempt under Section 80C of Income Tax Act. Maturity payouts from LIC policies are 100 percent Tax Free under Section 10(10D). Post Office PPF and SSY are also EEE tax free.",
                "metadata": {"type": "tax_guide"}
            },
            {
                "id": "kb_lic_vs_post_office",
                "title": "LIC vs Post Office Comparison",
                "content": "Comparison LIC vs Post Office: LIC provides life risk cover sum assured plus annual bonus growth. Post Office provides fixed sovereign guaranteed high interest rates. Ideal financial planning requires a balance of both LIC for life cover and Post Office for liquid fixed returns.",
                "metadata": {"type": "comparison"}
            }
        ]

        for chunk in knowledge_chunks:
            self.documents.append(chunk)

        # 3. Build Token Vocab & Calculate IDF
        num_docs = len(self.documents)
        doc_tokens = []
        for doc in self.documents:
            tokens = self._tokenize(doc["content"])
            doc_tokens.append(tokens)
            self.vocabulary.update(tokens)

        # Calculate IDF (Inverse Document Frequency)
        self.idf = {}
        for token in self.vocabulary:
            doc_count = sum(1 for tokens in doc_tokens if token in tokens)
            self.idf[token] = math.log((num_docs + 1) / (doc_count + 1)) + 1.0

        # Calculate TF-IDF Vectors for all documents
        self.doc_vectors = []
        for tokens in doc_tokens:
            vec = self._vectorize(tokens)
            self.doc_vectors.append(vec)

        self.is_indexed = True

    def _vectorize(self, tokens):
        """Converts tokens into a normalized sparse vector embedding."""
        counts = Counter(tokens)
        total = len(tokens) or 1
        vector = {}
        norm_sq = 0.0
        
        for word, count in counts.items():
            if word in self.idf:
                tf = count / total
                tfidf = tf * self.idf[word]
                vector[word] = tfidf
                norm_sq += tfidf * tfidf

        # Normalize vector magnitude to unit vector
        norm = math.sqrt(norm_sq) or 1.0
        for word in vector:
            vector[word] /= norm

        return vector

    def _cosine_similarity(self, vec1, vec2):
        """Computes cosine similarity between two normalized sparse vectors."""
        similarity = 0.0
        for word, val1 in vec1.items():
            if word in vec2:
                similarity += val1 * vec2[word]
        return similarity

    def search(self, query, top_k=3):
        """
        Executes Vector Similarity Search for user query against vector database index.
        Returns top_k matching documents with confidence scores.
        """
        if not self.is_indexed:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        query_vec = self._vectorize(query_tokens)

        results = []
        for idx, doc_vec in enumerate(self.doc_vectors):
            sim = self._cosine_similarity(query_vec, doc_vec)
            if sim > 0.05:  # Relevance threshold
                results.append({
                    "document": self.documents[idx],
                    "similarity": round(sim, 4),
                    "confidence_percent": min(99, int(round(sim * 100 + 40)))
                })

        # Sort by similarity score descending
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

# Singleton Global Instance
vector_db_instance = SimpleVectorDB()
