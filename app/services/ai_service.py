import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import xgboost as xgb
from app.models.grade import Grade
import google.generativeai as genai 
class StudentAI:
    def __init__(self):
        self.df = None
        # Cấu hình API Key trực tiếp tại đây
        self.api_key = "key của bạn"
        genai.configure(api_key=self.api_key)
        self.model_name = "gemini-2.5-flash"

    def load_data_from_db(self, subject_id=None):
        """Lấy dữ liệu từ database, có thể lọc theo môn học"""
        if subject_id:
            grades = Grade.query.filter_by(subject_id=subject_id).all()
        else:
            grades = Grade.query.all()
            
        data = []
        for g in grades:
            mid = g.midterm_score if g.midterm_score is not None else 0
            fin = g.final_score if g.final_score is not None else 0
            # Tự tính tổng kết nếu null
            total = g.subject_score if g.subject_score is not None else (0.4 * mid + 0.6 * fin)
            
            s_name = g.student.full_name if (g.student and hasattr(g.student, 'full_name')) else f"SV_{g.student_id}"
            sub_name = g.subject.name if (g.subject and hasattr(g.subject, 'name')) else "N/A"

            data.append({
                'Mã SV': g.student_id,
                'Tên': s_name,
                'Môn': sub_name,
                'Điểm GK': mid,
                'Điểm CK': fin,
                'Tổng Kết': round(total, 2) # Làm tròn cho đẹp
            })
        
        self.df = pd.DataFrame(data)
        return self.df

    def analyze_students(self, subject_id=None):
        """Hàm phân tích thống kê (Giữ nguyên logic của bạn)"""
        if self.df is None or self.df.empty or subject_id is not None:
            self.load_data_from_db(subject_id)
        
        if self.df.empty: return pd.DataFrame()

        # --- 1. Phân nhóm (K-Means) ---
        X = self.df[['Điểm GK', 'Điểm CK']].fillna(0)
        so_luong_sv = len(self.df)
        n_clusters = min(3, so_luong_sv)
        
        if n_clusters < 2:
            self.df['Phân Loại'] = "Chưa đủ dữ liệu"
            self.df['Nhóm ID'] = 0
        else:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            self.df['Nhóm ID'] = kmeans.fit_predict(X)
            
            # Gán nhãn dựa trên điểm trung bình của nhóm
            means = self.df.groupby('Nhóm ID')['Tổng Kết'].mean().sort_values()
            sorted_clusters = means.index.tolist()
            
            labels = {}
            for i, cluster_id in enumerate(sorted_clusters):
                if i == 0: labels[cluster_id] = 'Cần Cải Thiện'
                elif i == len(sorted_clusters) - 1: labels[cluster_id] = 'Giỏi'
                else: labels[cluster_id] = 'Khá'
            
            self.df['Phân Loại'] = self.df['Nhóm ID'].map(labels)

        # --- 2. Dự báo Rớt (XGBoost) ---
        self.df['Rớt Môn'] = (self.df['Tổng Kết'] < 4.0).astype(int)
        
        if len(self.df) > 5: # Chỉ chạy ML khi đủ dữ liệu
            try:
                model = xgb.XGBClassifier(eval_metric='logloss', use_label_encoder=False)
                model.fit(self.df[['Điểm GK']], self.df['Rớt Môn'])
                # Fix lỗi dimension
                probs = model.predict_proba(self.df[['Điểm GK']])[:, 1]
                self.df['Nguy Cơ Rớt (%)'] = (probs * 100).round(1)
            except Exception as e:
                print(f"Lỗi XGBoost: {e}")
                self.df['Nguy Cơ Rớt (%)'] = 0.0
        else:
            self.df['Nguy Cơ Rớt (%)'] = 0.0

        return self.df

    def chat_with_data(self, question):
        """
        CÁCH MỚI: Gửi trực tiếp dữ liệu dạng text cho Gemini.
        Bỏ qua PandasAI để tránh lỗi model.
        """
        try:
            if self.df is None or self.df.empty:
                self.load_data_from_db()
            
            if self.df.empty:
                return "Không có dữ liệu điểm số nào để phân tích."

            # 1. Chuyển DataFrame thành chuỗi CSV (hoặc Markdown) để AI đọc được
            # Giới hạn 50 dòng đầu nếu dữ liệu quá lớn để tiết kiệm token
            data_str = self.df.head(60).to_csv(index=False)

            # 2. Tạo Prompt (Câu lệnh gửi cho AI)
            prompt = f"""
            Bạn là một trợ lý AI phân tích dữ liệu điểm thi.
            Dưới đây là dữ liệu điểm của sinh viên (định dạng CSV):
            
            {data_str}
            
            Hãy trả lời câu hỏi sau dựa trên dữ liệu trên: "{question}"
            
            Lưu ý: 
            - Trả lời ngắn gọn, đi thẳng vào vấn đề.
            - Nếu câu hỏi liên quan đến thống kê, hãy tính toán chính xác.
            - Trả lời bằng tiếng Việt.
            """

            # 3. Gọi Gemini Model trực tiếp
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            
            return response.text

        except Exception as e:
            print(f"Lỗi chat AI: {e}")
            return f"Xin lỗi, AI đang bận hoặc gặp lỗi kết nối: {str(e)}"