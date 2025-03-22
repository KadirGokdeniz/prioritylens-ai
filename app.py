import os
import gradio as gr
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import datetime

# Veritabanı bağlantı bilgilerini alma
DATABASE_URL = "postgresql://postgres:qeqe@localhost:5432/prioritylens"
# Veritabanı bağlantı fonksiyonu
def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Veritabanı bağlantısında hata: {e}")
        return None

# Veritabanı tablolarını oluştur (eğer yoksa)
def create_tables_if_not_exist():
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            # Users tablosu
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
            """)
            
            # Projects tablosu
            cur.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
            """)
            
            # Tasks tablosu
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    project_id INTEGER REFERENCES projects(id),
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    impact_score INTEGER NOT NULL CHECK (impact_score BETWEEN 1 AND 10),
                    urgency_score INTEGER NOT NULL CHECK (urgency_score BETWEEN 1 AND 10),
                    effort_score INTEGER NOT NULL CHECK (effort_score BETWEEN 1 AND 10),
                    alignment_score INTEGER NOT NULL CHECK (alignment_score BETWEEN 1 AND 10),
                    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
                    due_date DATE,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
            """)
            
            conn.commit()
            return True
    except Exception as e:
        print(f"Tablo oluşturmada hata: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# Örnek kullanıcı oluştur (sadece test amaçlı)
def create_demo_user():
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor() as cur:
            # Kullanıcıyı kontrol et
            cur.execute("SELECT id FROM users WHERE username = %s", ("demo_user",))
            user = cur.fetchone()
            
            if not user:
                # Kullanıcı yoksa oluştur
                cur.execute("""
                    INSERT INTO users (username, email, password_hash)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, ("demo_user", "demo@example.com", "demo_password_hash"))
                user_id = cur.fetchone()[0]
                conn.commit()
                return user_id
            else:
                return user[0]
    except Exception as e:
        print(f"Demo kullanıcı oluşturmada hata: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

# Proje ekleme fonksiyonu
def add_project(user_id, name, description=""):
    conn = get_db_connection()
    if not conn:
        return False, "Veritabanı bağlantısı kurulamadı"
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO projects (user_id, name, description)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (user_id, name, description))
            project_id = cur.fetchone()[0]
            conn.commit()
            return True, f"Proje başarıyla eklendi! ID: {project_id}"
    except Exception as e:
        conn.rollback()
        return False, f"Proje eklenirken hata oluştu: {e}"
    finally:
        conn.close()

# Görev ekleme fonksiyonu
def add_task(project_id, name, description, impact_score, urgency_score, effort_score, alignment_score, due_date=None):
    conn = get_db_connection()
    if not conn:
        return False, "Veritabanı bağlantısı kurulamadı"
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tasks (project_id, name, description, impact_score, urgency_score, effort_score, alignment_score, due_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (project_id, name, description, impact_score, urgency_score, effort_score, alignment_score, due_date))
            task_id = cur.fetchone()[0]
            conn.commit()
            return True, f"Görev başarıyla eklendi! ID: {task_id}"
    except Exception as e:
        conn.rollback()
        return False, f"Görev eklenirken hata oluştu: {e}"
    finally:
        conn.close()

# Projeleri getir
def get_projects(user_id):
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, name, description, is_active
                FROM projects
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))
            return cur.fetchall()
    except Exception as e:
        print(f"Projeleri getirirken hata: {e}")
        return []
    finally:
        conn.close()

# Proje için görevleri getir
def get_tasks(project_id):
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, name, description, impact_score, urgency_score, effort_score, alignment_score, status, due_date
                FROM tasks
                WHERE project_id = %s
                ORDER BY created_at DESC
            """, (project_id,))
            return cur.fetchall()
    except Exception as e:
        print(f"Görevleri getirirken hata: {e}")
        return []
    finally:
        conn.close()

# Pareto puanı hesaplama
def calculate_pareto_score(impact, urgency, alignment, effort):
    # Etki ve Aciliyet pozitif, Çaba ise negatif etkisi var
    # Stratejik uyum pozitif etki eder
    value = (impact * 0.4) + (urgency * 0.3) + (alignment * 0.3)
    efficiency = value / effort if effort > 0 else value
    return efficiency * 10  # 0-100 arası bir puana dönüştür

# Pareto analizi yap
def perform_pareto_analysis(tasks):
    if not tasks:
        return None, None
    
    df = pd.DataFrame(tasks)
    
    # Pareto skoru hesapla
    df['pareto_score'] = df.apply(lambda row: calculate_pareto_score(
        row['impact_score'], row['urgency_score'], row['alignment_score'], row['effort_score']), axis=1)
    
    # Skorları büyükten küçüğe sırala
    df = df.sort_values('pareto_score', ascending=False)
    
    # Kümülatif toplam ve yüzde hesapla
    total_score = df['pareto_score'].sum()
    df['cumulative_score'] = df['pareto_score'].cumsum()
    df['score_percentage'] = df['pareto_score'] / total_score * 100
    df['cumulative_percentage'] = df['cumulative_score'] / total_score * 100
    
    # Pareto grafiği oluştur
    fig = go.Figure()
    
    # Bar grafiği - Pareto skorları
    fig.add_trace(go.Bar(
        x=df['name'],
        y=df['pareto_score'],
        name='Pareto Skoru',
        marker_color='#3498db'
    ))
    
    # Çizgi grafiği - Kümülatif yüzde
    fig.add_trace(go.Scatter(
        x=df['name'],
        y=df['cumulative_percentage'],
        name='Kümülatif Yüzde',
        marker_color='#e74c3c',
        mode='lines+markers',
        yaxis='y2'
    ))
    
    # 80% çizgisi
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=80,
        x1=len(df)-0.5,
        y1=80,
        line=dict(color="red", width=2, dash="dash"),
        yref='y2'
    )
    
    # Grafik düzeni
    fig.update_layout(
        title='Pareto Analizi: Görevlerin Etki/Çaba Dağılımı',
        xaxis_title='Görevler',
        yaxis_title='Pareto Skoru',
        yaxis2=dict(
            title='Kümülatif Yüzde (%)',
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=600,
        bargap=0.15
    )
    
    # Dört çeyrek matris grafiği
    quadrant_fig = px.scatter(
        df,
        x='effort_score',
        y='impact_score',
        size='urgency_score',
        color='pareto_score',
        color_continuous_scale='Viridis',
        hover_name='name',
        size_max=20,
        labels={
            'effort_score': 'Çaba (1-10)',
            'impact_score': 'Etki (1-10)',
            'urgency_score': 'Aciliyet',
            'pareto_score': 'Pareto Skoru'
        },
        title='Dört Çeyrek Analizi: Etki vs Çaba'
    )
    
    # Çeyrek bölümleri için dikey ve yatay çizgiler
    quadrant_fig.add_shape(
        type="line",
        x0=5.5,
        y0=0,
        x1=5.5,
        y1=10,
        line=dict(color="gray", width=1, dash="dash")
    )
    
    quadrant_fig.add_shape(
        type="line",
        x0=0,
        y0=5.5,
        x1=10,
        y1=5.5,
        line=dict(color="gray", width=1, dash="dash")
    )
    
    # Çeyrek etiketleri
    quadrant_fig.add_annotation(x=3, y=8, text="HEMEN YAP", showarrow=False, font=dict(size=14, color="green"))
    quadrant_fig.add_annotation(x=8, y=8, text="PLANLA", showarrow=False, font=dict(size=14, color="blue"))
    quadrant_fig.add_annotation(x=3, y=3, text="DELEGASYON", showarrow=False, font=dict(size=14, color="orange"))
    quadrant_fig.add_annotation(x=8, y=3, text="ELEME", showarrow=False, font=dict(size=14, color="red"))
    
    quadrant_fig.update_layout(height=600)
    
    return fig, quadrant_fig

# Önceliklendirme önerileri
def get_recommendations(tasks):
    if not tasks:
        return "Henüz görev eklenmemiş. Öncelik önerileri için görev ekleyin."
    
    df = pd.DataFrame(tasks)
    
    # Pareto skoru hesapla
    df['pareto_score'] = df.apply(lambda row: calculate_pareto_score(
        row['impact_score'], row['urgency_score'], row['alignment_score'], row['effort_score']), axis=1)
    
    # Skorları büyükten küçüğe sırala
    df = df.sort_values('pareto_score', ascending=False)
    
    # Kümülatif toplam ve yüzde hesapla
    total_score = df['pareto_score'].sum()
    df['cumulative_score'] = df['pareto_score'].cumsum()
    df['cumulative_percentage'] = df['cumulative_score'] / total_score * 100
    
    # 80% eşiğini bul
    top_tasks = df[df['cumulative_percentage'] <= 80]
    if len(top_tasks) == 0:
        top_tasks = df.iloc[:1]  # En azından bir görev
    
    # Görev sayısı
    total_tasks = len(df)
    top_task_count = len(top_tasks)
    percentage = (top_task_count / total_tasks) * 100
    
    recommendations = f"""
    # 📊 Pareto Prensibi Analizi

    ## 🔍 Özet
    Toplam {total_tasks} görev arasından, sadece {top_task_count} görev (%{percentage:.1f}) sonuçların %80'ini oluşturuyor.
    
    ## 🎯 Öncelikli Görevler
    Zamanınızın çoğunu şu görevlere ayırmalısınız:
    """
    
    for i, task in enumerate(top_tasks.itertuples(), 1):
        recommendations += f"\n{i}. **{task.name}** (Pareto Skoru: {task.pareto_score:.1f})"
    
    # Dört çeyrek analizi için öneriler
    recommendations += """
    
    ## 📋 Eylem Planı
    
    ### ✅ HEMEN YAP (Yüksek Etki, Düşük Çaba)
    """
    
    high_impact_low_effort = df[(df['impact_score'] > 5) & (df['effort_score'] <= 5)]
    if len(high_impact_low_effort) > 0:
        for task in high_impact_low_effort.itertuples():
            recommendations += f"\n- **{task.name}**"
    else:
        recommendations += "\n- Bu kategoride görev bulunamadı."
    
    recommendations += """
    
    ### 📅 PLANLA (Yüksek Etki, Yüksek Çaba)
    """
    
    high_impact_high_effort = df[(df['impact_score'] > 5) & (df['effort_score'] > 5)]
    if len(high_impact_high_effort) > 0:
        for task in high_impact_high_effort.itertuples():
            recommendations += f"\n- **{task.name}**"
    else:
        recommendations += "\n- Bu kategoride görev bulunamadı."
    
    recommendations += """
    
    ### 👥 DELEGASYON (Düşük Etki, Düşük Çaba)
    """
    
    low_impact_low_effort = df[(df['impact_score'] <= 5) & (df['effort_score'] <= 5)]
    if len(low_impact_low_effort) > 0:
        for task in low_impact_low_effort.itertuples():
            recommendations += f"\n- **{task.name}**"
    else:
        recommendations += "\n- Bu kategoride görev bulunamadı."
    
    recommendations += """
    
    ### ❌ ELEME (Düşük Etki, Yüksek Çaba)
    """
    
    low_impact_high_effort = df[(df['impact_score'] <= 5) & (df['effort_score'] > 5)]
    if len(low_impact_high_effort) > 0:
        for task in low_impact_high_effort.itertuples():
            recommendations += f"\n- **{task.name}**"
    else:
        recommendations += "\n- Bu kategoride görev bulunamadı."
    
    return recommendations

# Ana uygulama fonksiyonu
def prioritylens_app():
    # Demo kullanıcı oluştur
    create_tables_if_not_exist()
    user_id = create_demo_user()
    
    if user_id is None:
        return gr.Markdown("Veritabanına bağlantı kurulamadı veya demo kullanıcı oluşturulamadı!")
    
    with gr.Blocks(title="PriorityLens-AI: Pareto Prensibi Temelli İş Önceliklendirme") as app:
        gr.Markdown("""
        # 🎯 PriorityLens-AI
        ## Pareto Prensibi Temelli İş Önceliklendirme Sistemi
        
        İş yaşamınızdaki görevleri Pareto Prensibi (80/20 kuralı) ile analiz ederek, 
        zamanınızın %20'sini harcayarak sonuçların %80'ini elde edebileceğiniz görevleri belirleyin.
        """)
        
        with gr.Tab("Proje Yönetimi"):
            with gr.Row():
                with gr.Column(scale=1):
                    project_name_input = gr.Textbox(label="Proje Adı")
                    project_desc_input = gr.Textbox(label="Proje Açıklaması", lines=3)
                    project_add_btn = gr.Button("Proje Ekle", variant="primary")
                    project_status = gr.Markdown("")
                
                with gr.Column(scale=2):
                    projects_dropdown = gr.Dropdown(label="Projeler", choices=[], interactive=True)
                    refresh_projects_btn = gr.Button("Projeleri Yenile")
        
        with gr.Tab("Görev Yönetimi"):
            with gr.Row():
                with gr.Column():
                    task_name_input = gr.Textbox(label="Görev Adı")
                    task_desc_input = gr.Textbox(label="Görev Açıklaması", lines=2)
                    
                    with gr.Row():
                        impact_slider = gr.Slider(minimum=1, maximum=10, step=1, label="Etki Puanı (1-10)", value=5)
                        urgency_slider = gr.Slider(minimum=1, maximum=10, step=1, label="Aciliyet Puanı (1-10)", value=5)
                    
                    with gr.Row():
                        effort_slider = gr.Slider(minimum=1, maximum=10, step=1, label="Çaba Puanı (1-10)", value=5)
                        alignment_slider = gr.Slider(minimum=1, maximum=10, step=1, label="Stratejik Uyum Puanı (1-10)", value=5)
                    
                    due_date_input = gr.Textbox(label="Son Tarih (YYYY-MM-DD, opsiyonel)")
                    task_add_btn = gr.Button("Görev Ekle", variant="primary")
                    task_status = gr.Markdown("")
                
                with gr.Column():
                    tasks_table = gr.DataFrame(
                        headers=["ID", "Görev", "Etki", "Aciliyet", "Çaba", "Uyum", "Durum", "Son Tarih"],
                        label="Proje Görevleri"
                    )
                    refresh_tasks_btn = gr.Button("Görevleri Yenile")
        
        with gr.Tab("Pareto Analizi"):
            with gr.Row():
                analyze_btn = gr.Button("Pareto Analizi Yap", variant="primary")
            
            with gr.Row():
                pareto_plot = gr.Plot(label="Pareto Analizi")
                quadrant_plot = gr.Plot(label="Dört Çeyrek Analizi")
            
            with gr.Row():
                recommendations = gr.Markdown(label="Önceliklendirme Önerileri")
        
        # Projeleri listele
        def refresh_projects():
            projects = get_projects(user_id)
            choices = [(p['name'], p['id']) for p in projects]
            return gr.Dropdown(choices=choices)
        
        # Proje ekle
        def add_project_handler(name, description):
            if not name or name.strip() == "":
                return "Proje adı boş olamaz!"
            
            success, message = add_project(user_id, name, description)
            return message
        
        # Görevleri listele
        def refresh_tasks(project_id):
            if not project_id:
                return pd.DataFrame()
            
            tasks = get_tasks(project_id)
            if not tasks:
                return pd.DataFrame()
            
            task_df = pd.DataFrame([
                {
                    "ID": t['id'],
                    "Görev": t['name'],
                    "Etki": t['impact_score'],
                    "Aciliyet": t['urgency_score'],
                    "Çaba": t['effort_score'],
                    "Uyum": t['alignment_score'],
                    "Durum": t['status'],
                    "Son Tarih": t['due_date'].strftime('%Y-%m-%d') if t['due_date'] else ""
                }
                for t in tasks
            ])
            return task_df
        
        # Görev ekle
        def add_task_handler(project_id, name, description, impact, urgency, effort, alignment, due_date):
            if not project_id:
                return "Lütfen önce bir proje seçin!"
            
            if not name or name.strip() == "":
                return "Görev adı boş olamaz!"
            
            # Son tarih kontrolü
            parsed_date = None
            if due_date and due_date.strip() != "":
                try:
                    parsed_date = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
                except ValueError:
                    return "Son tarih formatı geçersiz! Lütfen YYYY-MM-DD formatında girin."
            
            success, message = add_task(
                project_id, name, description, 
                int(impact), int(urgency), int(effort), int(alignment), 
                parsed_date
            )
            return message
        
        # Analiz yap
        def analyze_tasks(project_id):
            if not project_id:
                return None, None, "Lütfen önce bir proje seçin!"
            
            tasks = get_tasks(project_id)
            if not tasks:
                return None, None, "Bu projede henüz görev bulunmuyor!"
            
            pareto_fig, quadrant_fig = perform_pareto_analysis(tasks)
            recommendations_text = get_recommendations(tasks)
            
            return pareto_fig, quadrant_fig, recommendations_text
        
        # Etkileşimleri tanımla
        project_add_btn.click(add_project_handler, [project_name_input, project_desc_input], [project_status])
        refresh_projects_btn.click(refresh_projects, [], [projects_dropdown])
        
        task_add_btn.click(
            add_task_handler, 
            [projects_dropdown, task_name_input, task_desc_input, impact_slider, urgency_slider, effort_slider, alignment_slider, due_date_input], 
            [task_status]
        )
        
        refresh_tasks_btn.click(refresh_tasks, [projects_dropdown], [tasks_table])
        projects_dropdown.change(refresh_tasks, [projects_dropdown], [tasks_table])
        
        analyze_btn.click(analyze_tasks, [projects_dropdown], [pareto_plot, quadrant_plot, recommendations])
        
        # Başlangıçta projeleri yükle
        app.load(refresh_projects, [], [projects_dropdown])
        
    return app

# Uygulamayı başlat
if __name__ == "__main__":
    app = prioritylens_app()
    app.launch()