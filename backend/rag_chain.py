from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.vector_store import VectorStore
from backend.config import Config
from backend.context_manager import ContextManager
from typing import List, Dict, Set
import re

class RAGChain:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=Config.GEMINI_MODEL,
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0.8,
            convert_system_message_to_human=True
        )
        
        self.vector_store = VectorStore()
        self.context_manager = ContextManager()
        self.chain = None
        self.setup_chain()
    
    def generate_query_variations(self, original_query: str) -> List[str]:
        """Generate multiple query variations to capture comprehensive information"""
        variations = [original_query]
        
        # Add contextual variations based on conversation history
        contextual_variations = self.context_manager.get_contextual_query_variations(original_query)
        variations.extend(contextual_variations)
        
        # Add contextual variations based on conversation history
        contextual_variations = self.context_manager.get_contextual_query_variations(original_query)
        variations.extend(contextual_variations)
        
        # Convert to lowercase for analysis
        query_lower = original_query.lower()
        
        # Legal topic mappings for comprehensive search
        legal_mappings = {
            'rape': ['sexual assault', 'sexual offence', 'sexual violence', 'consent', 'section 63', 'section 64', 'section 65', 'section 66', 'section 67', 'section 68'],
            'murder': ['homicide', 'culpable homicide', 'section 100', 'section 101', 'section 102', 'killing', 'death penalty'],
            'theft': ['stealing', 'section 303', 'section 304', 'property offence', 'larceny'],
            'fraud': ['cheating', 'section 318', 'section 319', 'deception', 'forgery'],
            'dowry': ['dowry death', 'section 85', 'section 86', 'harassment', 'matrimonial cruelty'],
            'corruption': ['bribery', 'public servant', 'misconduct', 'prevention of corruption'],
            'article': ['constitutional provision', 'fundamental right', 'directive principle'],
            'section': ['criminal provision', 'offence', 'punishment', 'penalty'],
            'constitution': ['fundamental rights', 'directive principles', 'constitutional law', 'article'],
            'nyaya sanhita': ['criminal law', 'bharatiya nyaya sanhita', 'bns', 'criminal code', 'penal code'],
            # Income Tax related mappings
            'income tax': ['tax deduction', 'taxable income', 'assessment', 'tds', 'advance tax', 'section 80c', 'section 80d', 'section 194', 'finance act'],
            'tax': ['income tax act 1961', 'tax rules 1962', 'deduction', 'exemption', 'assessment year', 'financial year'],
            'tds': ['tax deducted at source', 'section 194', 'withholding tax', 'tds certificate', 'form 16'],
            'deduction': ['section 80c', 'section 80d', 'section 80g', 'section 24', 'house property', 'investment'],
            'assessment': ['income tax assessment', 'scrutiny', 'notice', 'penalty', 'interest'],
            'salary': ['section 17', 'perquisites', 'allowances', 'professional tax', 'provident fund'],
            'capital gains': ['section 54', 'section 54f', 'ltcg', 'stcg', 'indexation'],
            'business income': ['section 28', 'section 37', 'depreciation', 'business expenses'],
            'finance act': ['budget', 'amendments', 'new provisions', 'tax rates', 'slabs']
        }
        
        # Add specific variations based on query content
        for key, synonyms in legal_mappings.items():
            if key in query_lower:
                for synonym in synonyms:
                    variations.append(f"{synonym} {original_query}")
                    variations.append(synonym)
        
        # Add document-specific queries
        if any(term in query_lower for term in ['rape', 'sexual', 'assault', 'consent']):
            variations.extend([
                "sexual offences bharatiya nyaya sanhita",
                "rape laws india criminal code",
                "consent sexual assault provisions",
                "punishment sexual violence",
                "section 63 64 65 66 67 68 bharatiya nyaya sanhita"
            ])
        
        if any(term in query_lower for term in ['article', 'constitution', 'fundamental']):
            variations.extend([
                "constitutional provisions fundamental rights",
                "indian constitution articles",
                "directive principles state policy",
                "fundamental duties constitution"
            ])
        
        # Add Income Tax specific queries
        if any(term in query_lower for term in ['tax', 'income', 'deduction', 'tds', 'assessment', 'salary', 'capital gains', 'business']):
            variations.extend([
                "income tax act 1961 provisions",
                "tax deduction rules 1962",
                "assessment procedures income tax",
                "tax compliance requirements",
                "deduction exemption provisions"
            ])
        
        # Add general legal search terms
        variations.extend([
            f"legal provisions {original_query}",
            f"indian law {original_query}",
            f"criminal law {original_query}",
            f"constitutional law {original_query}"
        ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for variation in variations:
            if variation.lower() not in seen:
                seen.add(variation.lower())
                unique_variations.append(variation)
        
        return unique_variations[:5]  # Limit to 5 focused variations for speed
    
    def setup_chain(self):
        """Setup the RAG chain with custom prompt"""
        
        prompt_template = """You are an expert legal assistant specializing in Indian Constitution and Bharatiya Nyaya Sanhita (BNS). 
        Use the following context from multiple legal documents to answer the user's question accurately and comprehensively.

        Context: {context}

        Question: {question}

        Instructions:
        1. Analyze ALL provided context from different documents (Constitution, Bharatiya Nyaya Sanhita, etc.)
        2. For criminal law questions (like rape, theft, murder), focus on Bharatiya Nyaya Sanhita sections and provisions
        3. For constitutional questions, focus on constitutional articles, fundamental rights, and directive principles
        4. Combine information from multiple sources when relevant
        5. Provide detailed explanations with proper structure using headings and bullet points
        6. Include specific section/article numbers and quote the exact legal text when available
        7. If information spans multiple documents, clearly organize by source
        8. Always specify which document (Constitution vs BNS) each provision comes from
        9. Provide practical implications, penalties, and legal significance
        10. If context is insufficient, clearly state what information is missing

        Format your response with:
        ## Main Topic
        ### From Indian Constitution (if applicable)
        - Article numbers and provisions
        ### From Bharatiya Nyaya Sanhita (if applicable)  
        - Section numbers and provisions
        ### Key Provisions
        - Direct quotes from legal text
        ### Penalties and Punishments (if applicable)
        ### Practical Implications

        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        retriever = self.vector_store.get_retriever(k=12)
        
        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
    
    def multi_query_retrieval(self, question: str) -> List[Dict]:
        """Perform multiple queries to gather comprehensive information"""
        print(f"Starting multi-query retrieval for: {question}")
        
        # Generate query variations
        query_variations = self.generate_query_variations(question)
        print(f"Generated {len(query_variations)} query variations")
        
        all_documents = []
        seen_content = set()
        
        for i, query in enumerate(query_variations):
            try:
                print(f"Executing query {i+1}/{len(query_variations)}: {query}")
                
                # Retrieve documents for this query variation
                docs = self.vector_store.similarity_search(query, k=8)
                
                # Add unique documents
                for doc in docs:
                    # Create a hash of the content to avoid duplicates
                    content_hash = hash(doc.page_content[:500])  # Use first 500 chars for uniqueness
                    
                    if content_hash not in seen_content:
                        seen_content.add(content_hash)
                        all_documents.append({
                            'content': doc.page_content,
                            'metadata': doc.metadata,
                            'query_used': query,
                            'relevance_score': i  # Lower index = higher relevance
                        })
                
            except Exception as e:
                print(f"Error in query variation {i+1}: {str(e)}")
                continue
        
        print(f"Retrieved {len(all_documents)} unique documents from multi-query search")
        return all_documents
    
    def query(self, question: str) -> dict:
        """Process user query with multi-query retrieval and return comprehensive response"""
        try:
            # Perform multi-query retrieval
            retrieved_docs = self.multi_query_retrieval(question)
            
            if not retrieved_docs:
                return {
                    "answer": "I apologize, but I couldn't find relevant information for your question in the available documents.",
                    "sources": []
                }
            
            # Sort documents by relevance and limit to top results
            retrieved_docs.sort(key=lambda x: x['relevance_score'])
            top_docs = retrieved_docs[:10]  # Use top 10 most relevant documents for focused response
            
            # Combine all content for comprehensive context
            combined_context = "\n\n---DOCUMENT SEPARATOR---\n\n".join([
                f"[Source: {doc['metadata'].get('file_name', 'Unknown')} - {doc['metadata'].get('document_type', 'Unknown')}]\n{doc['content']}"
                for doc in top_docs
            ])
            
            # Get conversation context
            conversation_context = self.context_manager.get_context_summary()
            is_follow_up = self.context_manager.is_follow_up_question(question)
            
            # Create engaging, story-like structured prompt with context awareness
            comprehensive_prompt = f"""You are a knowledgeable legal storyteller who explains Indian law in an engaging, narrative style. 
            You specialize in Constitution, Criminal Law (Bharatiya Nyaya Sanhita), and Income Tax Law.
            Transform complex legal information into an interesting story that people can easily understand and remember.

            {conversation_context}

            Current Context: {combined_context}

            Question: {question}
            
            {"[NOTE: This appears to be a follow-up question to our previous conversation. Please reference relevant previous topics when appropriate.]" if is_follow_up else ""}

            RESPONSE FORMAT (tell it like a story using this structure):

            **{question}**

            **🎯 The Story Begins:**
            [Start with an engaging 2-3 sentence narrative that sets the context. For tax queries: "In the world of Indian taxation, this provision tells an interesting story..." For criminal law: "In the landscape of criminal justice..." For constitutional law: "When our Constitution makers envisioned..."]

            **⚖️ The Legal Framework:**
            • **Section/Article [Number]:** [Tell what this law does in story form - "This provision acts as a guardian that..." or "This section serves as a bridge between..."]
            • **Section/Article [Number]:** [Continue the narrative style]

            **📖 How It Works in Real Life:**
            [Explain the law like you're telling someone a story about how it actually works in practice. 
            For tax: "Here's what happens during tax season...", "When you file your returns..."
            For criminal law: "When someone commits this offense...", "The legal process unfolds like this..."
            For constitutional law: "In everyday life, this right protects you by..."]

            **⚠️ The Consequences:**
            [Tell the story of consequences:
            For tax: "Those who don't comply face a journey through tax penalties...", "The tax department responds with..."
            For criminal law: "Those who break this law face...", "The justice system responds with..."
            For constitutional law: "When this right is violated, the remedy is..."]
            • [Specific consequences told as a story]
            • [Amounts/penalties presented as "the price they pay"]

            **💡 The Bigger Picture:**
            • [Key insight: "What makes this law special is..." or "The genius of this provision lies in..."]
            • [Important takeaway: "The real impact on society is..." or "For taxpayers/citizens, this means..."]
            • [Practical wisdom: "The smart approach is..." or "To stay compliant/protected..."]

            STORYTELLING RULES:
            - Write like you're explaining to a friend over coffee
            - Use engaging transitions between sections
            - Include specific legal references but explain them simply
            - Make it memorable with vivid descriptions
            - For tax queries, focus on practical compliance and benefits
            - For criminal law, focus on justice and protection
            - For constitutional law, focus on rights and freedoms
            - If this is a follow-up question, reference previous topics naturally
            - Build on previous conversation when relevant
            - Keep the narrative flowing naturally
            - Maximum 350 words to allow for storytelling
            - Use phrases like "Here's the interesting part...", "What's fascinating is...", "The law works like this..."
            - For follow-ups, use phrases like "Building on what we discussed...", "Related to our previous topic...", "This connects to..."
            """
            
            # Generate response using LLM
            response_text = self.llm.invoke(comprehensive_prompt).content
            
            # Clean up any potential HTML tags from the response
            import re
            response_text = re.sub(r'<[^>]+>', '', response_text)  # Remove any HTML tags
            
            # Format only the most relevant sources (top 3-5)
            sources = []
            unique_files = set()
            
            for doc in top_docs[:5]:  # Limit to top 5 sources
                file_name = doc['metadata'].get('file_name', 'Unknown')
                doc_type = doc['metadata'].get('document_type', 'Unknown')
                
                # Avoid duplicate files in sources
                if file_name not in unique_files:
                    unique_files.add(file_name)
                    
                    # Extract key information from content
                    content_preview = doc['content'][:150].replace('\n', ' ').strip()
                    if len(doc['content']) > 150:
                        content_preview += "..."
                    
                    source_info = {
                        "content": content_preview,
                        "metadata": {
                            "file_name": file_name,
                            "document_type": doc_type.replace('_', ' ').title(),
                            "page_number": doc['metadata'].get('page_number', 'N/A')
                        }
                    }
                    sources.append(source_info)
            
            # Save this exchange to context history
            self.context_manager.add_exchange(question, response_text, sources)
            
            return {
                "answer": response_text,
                "sources": sources,
                "session_id": self.context_manager.current_session_id,
                "is_follow_up": is_follow_up
            }
            
        except Exception as e:
            print(f"Error in comprehensive query processing: {str(e)}")
            return {
                "answer": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "sources": []
            }
    
    def start_new_conversation(self) -> str:
        """Start a new conversation session"""
        return self.context_manager.start_new_session()
    
    def load_conversation(self, session_id: str) -> bool:
        """Load an existing conversation session"""
        return self.context_manager.load_session(session_id)
    
    def get_conversation_history(self) -> List[Dict]:
        """Get current conversation history"""
        return self.context_manager.current_context
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """Get list of recent conversation sessions"""
        return self.context_manager.get_recent_sessions(limit)
    
    def clear_old_conversations(self, days_old: int = 30):
        """Clear old conversation sessions"""
        self.context_manager.clear_old_sessions(days_old)