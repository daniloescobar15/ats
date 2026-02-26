import requests
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import hashlib
import base64
import getpass
import os

# ---------------- ENCRYPTION/DECRYPTION ----------------

ENCRYPTED_API_KEY = '9MOrmufUS+QFwoODVq5I2/8EPSOFoaX5nPT23n41+IPlmLA='

def decrypt_api_key(password):
    """Decrypts the API key using the provided password."""
    try:
        key = hashlib.sha256(password.encode()).digest()
        encrypted_bytes = base64.b64decode(ENCRYPTED_API_KEY)
        decrypted = ''.join([chr(encrypted_bytes[i] ^ key[i % len(key)]) for i in range(len(encrypted_bytes))])
        return decrypted
    except Exception as e:
        raise ValueError(f"Error al desencriptar API_KEY: {str(e)}")

def get_api_key(password=None):
    """Gets the API key by asking for password or using provided password."""
    if password is None:
        # For command line use
        password = getpass.getpass("Ingresa el password para acceder al API_KEY: ")
    
    if password != "jeniffer":
        raise ValueError("Password incorrecto. Acceso denegado.")
    
    return decrypt_api_key(password)

def initialize_api_key(password=None):
    """Initializes the API_KEY and HEADERS with the provided password."""
    global API_KEY, HEADERS
    API_KEY = get_api_key(password)
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

# ---------------- CONFIG ----------------

OPENAI_BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"

# API_KEY will be initialized via initialize_api_key() function
# This allows it to be set from Streamlit or command line
API_KEY = None
HEADERS = None

# Try to initialize from environment or command line if not in Streamlit
if os.getenv('STREAMLIT') is None:
    try:
        initialize_api_key()
    except:
        pass  # Will be initialized later

# Load embedding model once
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# ---------------- LLM CALL ----------------

def call_llm(system_prompt, user_prompt, model_name=MODEL_NAME, temperature=0.3):
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature
    }

    response = requests.post(
        f"{OPENAI_BASE_URL}/v1/chat/completions",
        headers=HEADERS,
        json=payload
    )

    return response.json()["choices"][0]["message"]["content"]


# ---------------- LANGUAGE HELPER ----------------

def _language_instruction(language):
    """Returns the instruction for output language. language is 'es' or 'en'."""
    if language == "es":
        return "\n\nIMPORTANT: You must respond entirely in Spanish (Español). All sections, headings, and content must be in Spanish."
    return "\n\nIMPORTANT: You must respond entirely in English. All sections, headings, and content must be in English."


# ---------------- KEYWORD EXTRACTION (OPTIMIZED) ----------------

def extract_keywords(job_description, language="es"):
    system_prompt = """You are an expert HR analyst and ATS specialist with 15+ years of experience in talent acquisition across all industries. 
    Your expertise includes understanding how Applicant Tracking Systems parse and rank resumes based on keyword matching.
    You excel at identifying critical skills, competencies, certifications, and requirements that hiring managers prioritize, regardless of the field (HR, administration, sales, operations, etc.)."""

    user_prompt = f"""Analyze the following job description and extract ALL critical keywords and requirements that an ATS system would prioritize.

    Extract and categorize:
    1. **Hard Skills & Technical Competencies**: Specific skills, software tools, systems, methodologies, or technical knowledge required (e.g., HRIS systems, payroll software, recruitment platforms, data analysis tools, etc.)
    2. **Soft Skills & Behavioral Competencies**: Leadership, communication, problem-solving, teamwork, negotiation, conflict resolution, etc.
    3. **Certifications & Qualifications**: Required or preferred certifications, degrees, licenses, professional credentials
    4. **Industry-Specific Terms & Knowledge**: Domain knowledge, industry standards, regulations, best practices, specialized terminology
    5. **Experience Requirements**: Years of experience, specific role types, industry experience, company size experience, etc.

    Format your response as a structured list with clear categories. Be comprehensive and include variations of terms (e.g., "recruitment" and "talent acquisition", "HRIS" and "Human Resources Information System").

    JOB DESCRIPTION:
    {job_description}

    Provide a detailed, categorized list of all relevant keywords and requirements. Adapt your analysis to the specific field and role described.{_language_instruction(language)}"""
    
    return call_llm(system_prompt, user_prompt, temperature=0.2)


# ---------------- SIMILARITY SCORE ----------------

def calculate_similarity(cv_text, job_description):
    embeddings = embedding_model.encode([cv_text, job_description])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return round(score * 100, 2)


# ---------------- SKILLS MATCHING ANALYSIS (NEW) ----------------

def skills_matching_analysis(cv_text, job_description, language="es"):
    system_prompt = """You are a senior recruiter and career consultant specializing in skills assessment and candidate-job matching across all industries. 
    You have deep expertise in analyzing competencies (both hard and soft skills), transferable skills, and identifying skill gaps.
    Your analysis helps candidates understand exactly what they have and what they need to develop, whether in HR, administration, operations, or any other field."""

    user_prompt = f"""Perform a comprehensive skills matching analysis between the candidate's resume and the job description.

    Provide a detailed analysis in the following format:

    **SKILLS MATCHING REPORT**

    1. **MATCHED SKILLS** (Skills the candidate has that match the job):
       - List each matched skill
       - Indicate strength level (Strong/Moderate/Weak)
       - Show where it appears in the resume

    2. **PARTIAL MATCHES** (Related skills that could be emphasized):
       - Skills the candidate has that are related but not exact matches
       - Suggestions on how to reframe or emphasize these

    3. **MISSING CRITICAL SKILLS** (Required skills the candidate lacks):
       - Prioritize by importance (Critical/Important/Nice-to-have)
       - Suggest how to acquire or demonstrate these skills
       - Identify transferable skills that could compensate

    4. **SKILL GAP PRIORITY**:
       - Top 3-5 skills to focus on developing
       - Quick wins (skills that can be learned quickly)
       - Long-term development areas

    CANDIDATE RESUME:
    {cv_text}

    JOB DESCRIPTION:
    {job_description}

    Be specific, actionable, and prioritize recommendations.{_language_instruction(language)}"""
    
    return call_llm(system_prompt, user_prompt, temperature=0.3)


# ---------------- GAP ANALYSIS (OPTIMIZED) ----------------

def gap_analysis(cv_text, job_description, language="es"):
    system_prompt = """You are a senior career coach and recruiter with expertise in resume optimization and career development. 
    You specialize in identifying gaps between candidate profiles and job requirements, providing actionable insights that help candidates improve their marketability.
    Your analysis is thorough, constructive, and focuses on actionable improvements."""

    user_prompt = f"""Perform a comprehensive gap analysis comparing the candidate's resume with the job description.

    Provide a detailed analysis covering:

    1. **CRITICAL GAPS** (Must-have requirements missing):
       - List each critical gap
       - Explain why it matters for this role
       - Provide specific recommendations to address it

    2. **EXPERIENCE GAPS**:
       - Years of experience vs. required
       - Type of experience (industry, company size, role complexity)
       - How to frame existing experience to better match

    3. **SKILL REPRESENTATION GAPS**:
       - Skills present but weakly represented
       - Skills that need better emphasis or examples
       - Missing skill combinations or synergies

    4. **QUALIFICATION GAPS**:
       - Missing certifications, degrees, or credentials
       - Alternative ways to demonstrate competency
       - Which qualifications are most valuable to pursue

    5. **IMPROVEMENT OPPORTUNITIES**:
       - Quick improvements (wording, emphasis, formatting)
       - Medium-term improvements (skill development, projects)
       - Long-term career development suggestions

    6. **STRENGTHS TO LEVERAGE**:
       - Unique strengths that differentiate the candidate
       - How to better highlight these in the resume

    CANDIDATE RESUME:
    {cv_text}

    JOB DESCRIPTION:
    {job_description}

    Be specific, prioritize by impact, and provide actionable recommendations.{_language_instruction(language)}"""
    
    return call_llm(system_prompt, user_prompt, temperature=0.3)


# ---------------- QUANTIFIABLE ACHIEVEMENTS ANALYSIS (NEW) ----------------

def analyze_achievements(cv_text, language="es"):
    system_prompt = """You are an expert resume writer specializing in quantifying achievements and impact. 
    You understand that recruiters and ATS systems prioritize resumes with measurable results, metrics, and concrete outcomes.
    You help candidates transform vague descriptions into powerful, quantifiable statements."""

    user_prompt = f"""Analyze the candidate's resume for quantifiable achievements and provide recommendations.

    Provide:

    1. **CURRENT QUANTIFIABLE ACHIEVEMENTS**:
       - List all achievements that already include numbers, percentages, metrics
       - Rate their effectiveness (Strong/Moderate/Weak)
       - Suggest improvements if needed

    2. **ACHIEVEMENTS THAT NEED QUANTIFICATION**:
       - Identify statements that are vague or lack metrics
       - Suggest specific numbers, percentages, or metrics to add
       - Provide example rewrites with quantifiable data

    3. **MISSING ACHIEVEMENT TYPES**:
       - Business impact: revenue impact, cost savings, budget management, efficiency improvements
       - People impact: team size managed, recruitment numbers, employee satisfaction scores, training programs delivered
       - Process impact: process improvements, time savings, quality improvements, compliance achievements
       - Scale impact: number of projects, clients served, transactions processed, reports generated
       - Suggest what types of metrics would strengthen the resume based on the role type

    4. **ACTIONABLE RECOMMENDATIONS**:
       - Specific ways to quantify each role/achievement based on the field (HR, administration, operations, etc.)
       - Industry-appropriate metrics for their specific field
       - How to estimate metrics if exact numbers aren't available
       - Examples of quantifiable achievements relevant to their role type

    CANDIDATE RESUME:
    {cv_text}

    Focus on making achievements more impactful and ATS-friendly through quantification.{_language_instruction(language)}"""
    
    return call_llm(system_prompt, user_prompt, temperature=0.3)


# ---------------- ACTION VERBS ANALYSIS (NEW) ----------------

def analyze_action_verbs(cv_text, job_description, language="es"):
    system_prompt = """You are a professional resume writer and career coach specializing in powerful language and action verbs.
    You understand that strong action verbs make resumes more compelling and help candidates stand out in ATS systems.
    You provide specific, industry-appropriate verb suggestions that align with job requirements."""

    user_prompt = f"""Analyze the action verbs used in the candidate's resume and provide recommendations.

    Provide:

    1. **CURRENT ACTION VERBS ANALYSIS**:
       - List verbs currently used
       - Rate their strength (Strong/Moderate/Weak/Overused)
       - Identify repetitive or weak verbs

    2. **RECOMMENDED ACTION VERBS**:
       - Industry-specific powerful verbs aligned with the job description
       - Verbs that match the job's requirements and tone
       - Verbs that demonstrate leadership, impact, innovation, etc.

    3. **VERB REPLACEMENT SUGGESTIONS**:
       - Specific weak verbs to replace
       - Suggested stronger alternatives
       - Example rewrites showing the improvement

    4. **VERB DIVERSITY**:
       - Identify if verbs are too repetitive
       - Suggest variety while maintaining clarity
       - Provide a list of 20-30 powerful verbs relevant to this role

    CANDIDATE RESUME:
    {cv_text}

    JOB DESCRIPTION:
    {job_description}

    Make the resume more dynamic and impactful through better verb choices.{_language_instruction(language)}"""
    
    return call_llm(system_prompt, user_prompt, temperature=0.3)


# ---------------- EXPERIENCE LEVEL ANALYSIS (NEW) ----------------

def analyze_experience_level(cv_text, job_description, language="es"):
    system_prompt = """You are a senior recruiter and career analyst with expertise in assessing candidate experience levels and career progression.
    You understand how to match candidate experience with job requirements and identify if a candidate is underqualified, well-matched, or overqualified.
    You provide insights on how to position experience effectively."""

    user_prompt = f"""Analyze the candidate's experience level relative to the job requirements.

    Provide:

    1. **EXPERIENCE LEVEL ASSESSMENT**:
       - Overall match: Underqualified / Well-matched / Overqualified
       - Years of experience comparison
       - Role complexity and seniority assessment

    2. **EXPERIENCE STRENGTHS**:
       - Relevant experience that strongly matches requirements
       - Unique experiences that add value
       - Transferable experience from other roles/industries

    3. **EXPERIENCE GAPS**:
       - Missing experience types or durations
       - How to frame existing experience to better match
       - Alternative experiences that demonstrate similar competencies

    4. **POSITIONING RECOMMENDATIONS**:
       - How to emphasize relevant experience
       - How to de-emphasize or reframe overqualification (if applicable)
       - How to address underqualification through skills and achievements

    5. **CAREER PROGRESSION ANALYSIS**:
       - Does the resume show clear career progression?
       - Are there gaps or inconsistencies?
       - How to better present career trajectory

    CANDIDATE RESUME:
    {cv_text}

    JOB DESCRIPTION:
    {job_description}

    Provide actionable insights on experience positioning.{_language_instruction(language)}"""
    
    return call_llm(system_prompt, user_prompt, temperature=0.3)


# ---------------- FORMAT & STRUCTURE RECOMMENDATIONS (NEW) ----------------

def analyze_format_structure(cv_text, job_description, language="es"):
    system_prompt = """You are an ATS optimization expert and resume formatting specialist.
    You understand how different ATS systems parse resumes and what formatting choices maximize compatibility and readability.
    You provide specific recommendations for resume structure, sections, and formatting that improve both ATS parsing and human readability."""

    user_prompt = f"""Analyze the resume's format, structure, and ATS compatibility.

    Provide:

    1. **ATS COMPATIBILITY ASSESSMENT**:
       - Overall ATS-friendliness score and issues
       - Formatting problems that could cause parsing errors
       - Recommendations for ATS-optimized formatting

    2. **STRUCTURE ANALYSIS**:
       - Are sections clearly defined and properly ordered?
       - Is information easy to find and parse?
       - Missing or unnecessary sections
       - Recommended section order for this role

    3. **FORMATTING RECOMMENDATIONS**:
       - Font choices, sizing, spacing
       - Use of headers, bullet points, bold text
       - Tables, columns, graphics (if any - usually problematic)
       - File format recommendations

    4. **CONTENT ORGANIZATION**:
       - Is information prioritized correctly?
       - Is the most relevant information prominent?
       - Recommendations for reordering or restructuring

    5. **LENGTH & DENSITY**:
       - Is the resume an appropriate length?
       - Is information too dense or too sparse?
       - Recommendations for condensing or expanding

    CANDIDATE RESUME:
    {cv_text}

    JOB DESCRIPTION:
    {job_description}

    Focus on both ATS compatibility and human readability.{_language_instruction(language)}"""
    
    return call_llm(system_prompt, user_prompt, temperature=0.3)


# ---------------- REWRITE CV (OPTIMIZED) ----------------

def rewrite_cv(cv_text, job_description, gap_analysis_text=None, language="es"):
    system_prompt = """You are a world-class ATS resume optimizer and professional resume writer with expertise in:
    - Applicant Tracking System optimization and keyword integration
    - Creating compelling, achievement-focused resume content
    - Industry best practices for resume writing
    - Balancing ATS optimization with human readability
    - Addressing skill gaps and experience gaps through strategic resume positioning
    
    Your resumes consistently pass ATS filters while remaining compelling to human recruiters. You maintain complete truthfulness and never fabricate information. You excel at strategically reframing existing experience to address identified gaps."""

    # Build the gap analysis section if provided
    gap_analysis_section = ""
    if gap_analysis_text:
        gap_analysis_section = f"""

    **CRITICAL: GAP ANALYSIS INSIGHTS** (Use these insights to guide your optimization):
    
    The following gap analysis has been performed comparing the candidate's resume with the job requirements. 
    You MUST use these insights to strategically improve the resume:
    
    {gap_analysis_text}
    
    **SPECIFIC INSTRUCTIONS BASED ON GAP ANALYSIS**:
    
    1. **ADDRESS CRITICAL GAPS**: 
       - For each critical gap identified, find ways to reframe existing experience to demonstrate related competencies
       - Emphasize transferable skills that compensate for missing requirements
       - Use strategic language that bridges identified gaps without fabricating experience
    
    2. **ENHANCE WEAKLY REPRESENTED SKILLS**:
       - If the gap analysis shows skills are present but weakly represented, strengthen their presentation
       - Add more specific examples and achievements related to these skills
       - Use stronger action verbs and quantifiable metrics for these areas
    
    3. **FRAME EXPERIENCE TO MATCH REQUIREMENTS**:
       - If experience gaps are identified, reframe existing roles to highlight relevant aspects
       - Emphasize the most relevant parts of each position
       - Use terminology from the job description that aligns with the candidate's actual experience
    
    4. **LEVERAGE IDENTIFIED STRENGTHS**:
       - Amplify the strengths mentioned in the gap analysis
       - Make these differentiating factors more prominent in the resume
       - Use them to compensate for areas where gaps exist
    
    5. **ADDRESS QUALIFICATION GAPS**:
       - If certifications or qualifications are missing, emphasize alternative ways the candidate demonstrates competency
       - Highlight relevant experience, projects, or skills that show equivalent knowledge
       - Use language that demonstrates proficiency even without formal credentials
    
    6. **IMPLEMENT QUICK IMPROVEMENTS**:
       - Apply all quick improvement recommendations from the gap analysis
       - Enhance wording, emphasis, and formatting as suggested
       - Make the resume more impactful in areas where gaps were identified
    
    Remember: You must address the gaps strategically while maintaining complete accuracy. Never fabricate experience, but do reframe and emphasize existing experience to better match requirements."""

    user_prompt = f"""Rewrite and optimize this resume to maximize ATS alignment and impact while maintaining complete accuracy.
{gap_analysis_section}

    OPTIMIZATION REQUIREMENTS:

    1. **ATS OPTIMIZATION**:
       - Integrate relevant keywords from the job description naturally
       - Use standard section headers (Experience, Education, Skills, etc.)
       - Ensure ATS-friendly formatting (no tables, complex graphics, or unusual characters)
       - Use standard date formats and clear structure

    2. **CONTENT ENHANCEMENT**:
       - Start each bullet point with a strong, varied action verb
       - Quantify achievements with specific numbers, percentages, metrics, and timeframes
       - Focus on impact and results, not just responsibilities
       - Use industry-standard terminology from the job description

    3. **STRUCTURE & FORMATTING**:
       - Clear, logical section order (Contact, Summary/Objective, Experience, Education, Skills, etc.)
       - Consistent formatting throughout
       - Easy-to-scan bullet points (not paragraphs)
       - Professional, clean appearance

    4. **KEYWORD INTEGRATION**:
       - Naturally incorporate important keywords from the job description
       - Use variations of key terms where appropriate
       - Ensure skills section matches job requirements
       - Include relevant tools, systems, software, methodologies, and industry-specific terms mentioned in the job (e.g., HRIS systems, recruitment platforms, payroll software, project management tools, etc. - adapt to the specific field)

    5. **ACCURACY & TRUTHFULNESS**:
       - Maintain all factual information exactly as provided
       - Do not add, remove, or modify dates, companies, titles, or achievements
       - Only enhance wording and presentation, never fabricate content
       - Preserve the candidate's actual experience and accomplishments

    6. **JOB-SPECIFIC CUSTOMIZATION**:
       - Emphasize experience and skills most relevant to this specific role
       - Use language and terminology that matches the job description
       - Highlight transferable skills and experiences
       - Position the candidate as an ideal fit for this role

    CANDIDATE RESUME:
    {cv_text}

    TARGET JOB DESCRIPTION:
    {job_description}

    Provide the complete optimized resume, maintaining all original information while significantly enhancing presentation, impact, and ATS compatibility. 
    {"CRITICALLY IMPORTANT: Use the gap analysis insights above to strategically address identified gaps and improve the resume's alignment with job requirements. " if gap_analysis_text else ""}
    {"Write the entire optimized resume in Spanish (Español)." if language == "es" else "Write the entire optimized resume in English."}"""
    
    return call_llm(system_prompt, user_prompt, temperature=0.4)


# ---------------- OVERALL RECOMMENDATIONS (NEW) ----------------

def get_overall_recommendations(cv_text, job_description, language="es"):
    system_prompt = """You are a senior career coach and resume expert with comprehensive knowledge of resume optimization, ATS systems, and job market trends.
    You provide holistic, strategic recommendations that help candidates improve their overall resume quality and marketability.
    Your advice is practical, prioritized, and actionable."""

    user_prompt = f"""Provide comprehensive, prioritized recommendations for improving this resume.

    Structure your response as:

    **PRIORITY 1 - CRITICAL IMPROVEMENTS** (Do these first - highest impact):
    - List 3-5 most critical improvements
    - Explain why each matters
    - Provide specific, actionable steps

    **PRIORITY 2 - IMPORTANT ENHANCEMENTS** (Do these next - significant impact):
    - List 3-5 important improvements
    - Explain the benefit of each
    - Provide specific guidance

    **PRIORITY 3 - OPTIMIZATION OPPORTUNITIES** (Polish and refine):
    - Additional improvements for maximum impact
    - Fine-tuning recommendations
    - Best practices to implement

    **QUICK WINS** (Easy improvements with good ROI):
    - Simple changes that can be made immediately
    - Low effort, high impact modifications

    **LONG-TERM DEVELOPMENT** (Career growth suggestions):
    - Skills or experiences to develop over time
    - Certifications or qualifications to pursue
    - Projects or experiences that would strengthen the profile

    CANDIDATE RESUME:
    {cv_text}

    JOB DESCRIPTION:
    {job_description}

    Be specific, actionable, and prioritize by impact and effort required.{_language_instruction(language)}"""
    
    return call_llm(system_prompt, user_prompt, temperature=0.3)