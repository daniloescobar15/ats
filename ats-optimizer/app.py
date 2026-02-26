import streamlit as st
import os
os.environ['STREAMLIT'] = '1'

from optimizer import (
    extract_keywords,
    calculate_similarity,
    rewrite_cv,
    gap_analysis,
    skills_matching_analysis,
    analyze_achievements,
    analyze_action_verbs,
    analyze_experience_level,
    analyze_format_structure,
    get_overall_recommendations,
    initialize_api_key
)

st.set_page_config(
    page_title="ATS Resume Optimizer PRO", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🚀 ATS Resume Optimizer PRO</h1>', unsafe_allow_html=True)
st.markdown("### Optimiza tu hoja de vida con análisis completo y recomendaciones detalladas")

# Password protection
if 'api_initialized' not in st.session_state:
    st.session_state.api_initialized = False

if not st.session_state.api_initialized:
    st.markdown("---")
    st.markdown("### 🔐 Autenticación Requerida")
    password = st.text_input("Ingresa el password para acceder al sistema:", type="password")
    
    if st.button("🔓 Autenticar"):
        try:
            initialize_api_key(password)
            st.session_state.api_initialized = True
            st.success("✅ Autenticación exitosa!")
            st.rerun()
        except ValueError as e:
            st.error(f"❌ {str(e)}")
    
    st.stop()

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuración")
    st.markdown("---")
    st.markdown("### 🌐 Idioma del reporte")
    report_language = st.radio(
        "Idioma del reporte / Report language",
        options=["Español", "English"],
        index=0,
        label_visibility="collapsed"
    )
    lang_code = "es" if report_language == "Español" else "en"
    st.markdown("---")
    st.markdown("### 📋 Análisis a realizar")
    
    run_keywords = st.checkbox("🔑 Extracción de Keywords", value=True)
    run_similarity = st.checkbox("📊 Score de Similitud", value=True)
    run_skills = st.checkbox("🎯 Análisis de Habilidades", value=True)
    run_gaps = st.checkbox("🧠 Análisis de Brechas", value=True)
    run_achievements = st.checkbox("📈 Análisis de Logros", value=True)
    run_verbs = st.checkbox("💪 Análisis de Verbos de Acción", value=True)
    run_experience = st.checkbox("👔 Análisis de Nivel de Experiencia", value=True)
    run_format = st.checkbox("📐 Análisis de Formato", value=True)
    run_recommendations = st.checkbox("💡 Recomendaciones Generales", value=True)
    run_optimize = st.checkbox("✍️ CV Optimizado", value=True)

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Tu Hoja de Vida")
    cv_text = st.text_area(
        "Pega tu CV aquí", 
        height=400,
        help="Pega el contenido completo de tu hoja de vida",
        label_visibility="collapsed"
    )

with col2:
    st.subheader("💼 Descripción del Trabajo")
    jd_text = st.text_area(
        "Pega la descripción del trabajo aquí", 
        height=400,
        help="Pega la descripción completa del trabajo al que estás aplicando",
        label_visibility="collapsed"
    )

if st.button("🔎 Iniciar Análisis Completo", type="primary", use_container_width=True):
    if not cv_text or not jd_text:
        st.error("⚠️ Por favor, pega tanto tu CV como la descripción del trabajo.")
    else:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = {}
        
        # Calculate total steps
        total_steps = sum([
            run_keywords, run_similarity, run_skills, run_gaps, 
            run_achievements, run_verbs, run_experience, run_format, 
            run_recommendations, run_optimize
        ])
        current_step = 0
        
        try:
            # Keywords extraction
            if run_keywords:
                current_step += 1
                progress = current_step / total_steps
                progress_bar.progress(progress)
                status_text.text(f"🔍 [{current_step}/{total_steps}] Extrayendo keywords de la descripción del trabajo...")
                results['keywords'] = extract_keywords(jd_text, language=lang_code)
            
            # Similarity score
            if run_similarity:
                current_step += 1
                progress = current_step / total_steps
                progress_bar.progress(progress)
                status_text.text(f"⚖️ [{current_step}/{total_steps}] Calculando similitud semántica...")
                results['similarity'] = calculate_similarity(cv_text, jd_text)
            
            # Skills matching
            if run_skills:
                current_step += 1
                progress = current_step / total_steps
                progress_bar.progress(progress)
                status_text.text(f"🎯 [{current_step}/{total_steps}] Analizando matching de habilidades...")
                results['skills'] = skills_matching_analysis(cv_text, jd_text, language=lang_code)
            
            # Gap analysis
            if run_gaps:
                current_step += 1
                progress = current_step / total_steps
                progress_bar.progress(progress)
                status_text.text(f"🧠 [{current_step}/{total_steps}] Realizando análisis de brechas...")
                results['gaps'] = gap_analysis(cv_text, jd_text, language=lang_code)
            
            # Achievements analysis
            if run_achievements:
                current_step += 1
                progress = current_step / total_steps
                progress_bar.progress(progress)
                status_text.text(f"📈 [{current_step}/{total_steps}] Analizando logros cuantificables...")
                results['achievements'] = analyze_achievements(cv_text, language=lang_code)
            
            # Action verbs analysis
            if run_verbs:
                current_step += 1
                progress = current_step / total_steps
                progress_bar.progress(progress)
                status_text.text(f"💪 [{current_step}/{total_steps}] Analizando verbos de acción...")
                results['verbs'] = analyze_action_verbs(cv_text, jd_text, language=lang_code)
            
            # Experience level analysis
            if run_experience:
                current_step += 1
                progress = current_step / total_steps
                progress_bar.progress(progress)
                status_text.text(f"👔 [{current_step}/{total_steps}] Analizando nivel de experiencia...")
                results['experience'] = analyze_experience_level(cv_text, jd_text, language=lang_code)
            
            # Format analysis
            if run_format:
                current_step += 1
                progress = current_step / total_steps
                progress_bar.progress(progress)
                status_text.text(f"📐 [{current_step}/{total_steps}] Analizando formato y estructura...")
                results['format'] = analyze_format_structure(cv_text, jd_text, language=lang_code)
            
            # Overall recommendations
            if run_recommendations:
                current_step += 1
                progress = current_step / total_steps
                progress_bar.progress(progress)
                status_text.text(f"💡 [{current_step}/{total_steps}] Generando recomendaciones generales...")
                results['recommendations'] = get_overall_recommendations(cv_text, jd_text, language=lang_code)
            
            # CV optimization
            if run_optimize:
                current_step += 1
                progress = current_step / total_steps
                progress_bar.progress(progress)
                status_text.text(f"✍️ [{current_step}/{total_steps}] Optimizando CV para ATS...")
                # Pass gap analysis if available to improve the rewrite
                gap_analysis_text = results.get('gaps', None)
                results['optimized_cv'] = rewrite_cv(cv_text, jd_text, gap_analysis_text=gap_analysis_text, language=lang_code)
            
            # Complete
            progress_bar.progress(1.0)
            status_text.success("✅ ¡Análisis completo! Revisa los resultados a continuación.")
            
        except Exception as e:
            st.error(f"❌ Error durante el análisis: {str(e)}")
            st.exception(e)
        
        # Display results
        st.markdown("---")
        st.markdown("# 📊 Resultados del Análisis")
        
        # Similarity Score - Prominent display
        if run_similarity and 'similarity' in results:
            st.markdown("## 📊 Score de Compatibilidad ATS")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Similitud Semántica", f"{results['similarity']}%")
            with col2:
                if results['similarity'] >= 80:
                    st.success("🟢 Excelente Match")
                elif results['similarity'] >= 60:
                    st.warning("🟡 Match Moderado")
                else:
                    st.error("🔴 Match Bajo - Necesita Mejoras")
            with col3:
                st.info(f"💡 Objetivo: >75% para mejor visibilidad")
        
        # Keywords
        if run_keywords and 'keywords' in results:
            st.markdown("## 🔑 Keywords Extraídas de la Descripción del Trabajo")
            with st.expander("Ver keywords completas", expanded=True):
                st.markdown(results['keywords'])
        
        # Skills Matching
        if run_skills and 'skills' in results:
            st.markdown("## 🎯 Análisis de Matching de Habilidades")
            with st.expander("Ver análisis completo de habilidades", expanded=True):
                st.markdown(results['skills'])
        
        # Gap Analysis
        if run_gaps and 'gaps' in results:
            st.markdown("## 🧠 Análisis de Brechas (Gap Analysis)")
            with st.expander("Ver análisis de brechas", expanded=True):
                st.markdown(results['gaps'])
        
        # Achievements Analysis
        if run_achievements and 'achievements' in results:
            st.markdown("## 📈 Análisis de Logros Cuantificables")
            with st.expander("Ver análisis de logros", expanded=False):
                st.markdown(results['achievements'])
        
        # Action Verbs Analysis
        if run_verbs and 'verbs' in results:
            st.markdown("## 💪 Análisis de Verbos de Acción")
            with st.expander("Ver análisis de verbos", expanded=False):
                st.markdown(results['verbs'])
        
        # Experience Level Analysis
        if run_experience and 'experience' in results:
            st.markdown("## 👔 Análisis de Nivel de Experiencia")
            with st.expander("Ver análisis de experiencia", expanded=False):
                st.markdown(results['experience'])
        
        # Format Analysis
        if run_format and 'format' in results:
            st.markdown("## 📐 Análisis de Formato y Estructura")
            with st.expander("Ver análisis de formato", expanded=False):
                st.markdown(results['format'])
        
        # Overall Recommendations
        if run_recommendations and 'recommendations' in results:
            st.markdown("## 💡 Recomendaciones Generales Prioritizadas")
            with st.expander("Ver todas las recomendaciones", expanded=True):
                st.markdown(results['recommendations'])
        
        # Optimized CV
        if run_optimize and 'optimized_cv' in results:
            st.markdown("## ✍️ CV Optimizado para ATS")
            st.markdown("### Tu hoja de vida optimizada con mejoras para pasar filtros ATS")
            
            optimized_display = st.text_area(
                "CV Optimizado",
                results['optimized_cv'],
                height=500,
                label_visibility="collapsed"
            )
            
            st.download_button(
                label="⬇️ Descargar CV Optimizado",
                data=results['optimized_cv'],
                file_name="cv_optimizado_ats.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        # Build and offer full report download
        if lang_code == "es":
            report_title = "REPORTE COMPLETO - ATS Resume Optimizer"
            sec_similarity = "Score de similitud"
            sec_keywords = "Keywords extraídas"
            sec_skills = "Análisis de matching de habilidades"
            sec_gaps = "Análisis de brechas (Gap Analysis)"
            sec_achievements = "Análisis de logros cuantificables"
            sec_verbs = "Análisis de verbos de acción"
            sec_experience = "Análisis de nivel de experiencia"
            sec_format = "Análisis de formato y estructura"
            sec_recommendations = "Recomendaciones generales"
            sec_optimized = "CV optimizado para ATS"
        else:
            report_title = "FULL REPORT - ATS Resume Optimizer"
            sec_similarity = "Similarity Score"
            sec_keywords = "Extracted Keywords"
            sec_skills = "Skills Matching Analysis"
            sec_gaps = "Gap Analysis"
            sec_achievements = "Quantifiable Achievements Analysis"
            sec_verbs = "Action Verbs Analysis"
            sec_experience = "Experience Level Analysis"
            sec_format = "Format & Structure Analysis"
            sec_recommendations = "Overall Recommendations"
            sec_optimized = "Optimized CV for ATS"
        
        report_parts = [f"{report_title}\n", "=" * 60 + "\n"]
        if run_similarity and 'similarity' in results:
            report_parts.append(f"\n## {sec_similarity}\n{results['similarity']}%\n")
        if run_keywords and 'keywords' in results:
            report_parts.append(f"\n## {sec_keywords}\n{results['keywords']}\n")
        if run_skills and 'skills' in results:
            report_parts.append(f"\n## {sec_skills}\n{results['skills']}\n")
        if run_gaps and 'gaps' in results:
            report_parts.append(f"\n## {sec_gaps}\n{results['gaps']}\n")
        if run_achievements and 'achievements' in results:
            report_parts.append(f"\n## {sec_achievements}\n{results['achievements']}\n")
        if run_verbs and 'verbs' in results:
            report_parts.append(f"\n## {sec_verbs}\n{results['verbs']}\n")
        if run_experience and 'experience' in results:
            report_parts.append(f"\n## {sec_experience}\n{results['experience']}\n")
        if run_format and 'format' in results:
            report_parts.append(f"\n## {sec_format}\n{results['format']}\n")
        if run_recommendations and 'recommendations' in results:
            report_parts.append(f"\n## {sec_recommendations}\n{results['recommendations']}\n")
        if run_optimize and 'optimized_cv' in results:
            report_parts.append(f"\n## {sec_optimized}\n{results['optimized_cv']}\n")
        
        full_report = "\n".join(report_parts)
        report_filename = "reporte_completo_ats.txt" if lang_code == "es" else "full_report_ats.txt"
        
        st.markdown("---")
        st.markdown("### 📥 Descargar reporte completo")
        st.download_button(
            label="⬇️ Descargar reporte completo (todo el análisis)",
            data=full_report,
            file_name=report_filename,
            mime="text/plain",
            key="download_full_report",
            use_container_width=True
        )
        
        # Summary section
        st.markdown("---")
        st.markdown("## 📝 Resumen Ejecutivo")
        
        summary_col1, summary_col2 = st.columns(2)
        
        with summary_col1:
            st.markdown("### ✅ Fortalezas")
            if run_similarity and 'similarity' in results:
                if results['similarity'] >= 70:
                    st.success(f"• Buen match semántico ({results['similarity']}%)")
            if run_skills and 'skills' in results:
                st.info("• Revisa el análisis de habilidades para ver tus fortalezas")
        
        with summary_col2:
            st.markdown("### 🎯 Áreas de Mejora")
            if run_similarity and 'similarity' in results:
                if results['similarity'] < 70:
                    st.warning(f"• Mejorar match semántico (actual: {results['similarity']}%)")
            if run_gaps and 'gaps' in results:
                st.info("• Revisa el análisis de brechas para áreas específicas")
        
        st.markdown("---")
        st.success("🎉 ¡Análisis completo! Usa las recomendaciones para mejorar tu hoja de vida.")