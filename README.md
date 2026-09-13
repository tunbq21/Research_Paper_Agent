# 📄 Research Paper Agent

**Research Paper Agent** là một AI Agent tự động được thiết kế để tìm kiếm, phân tích, tóm tắt và trích xuất thông tin chuyên sâu từ các bài báo nghiên cứu khoa học.

Dự án này sử dụng kiến trúc AI Agent tiên tiến kết hợp với RAG (Retrieval-Augmented Generation) để xử lý các tài liệu học thuật (như PDF), giúp người dùng đọc và hiểu các bài nghiên cứu một cách nhanh chóng, chính xác và giảm thiểu rủi ro bị "hallucinate" (ảo giác) từ mô hình ngôn ngữ.

## 🌟 Tính năng chính

- **Xử lý PDF:** Đọc, phân tích và trích xuất nội dung từ các bài báo nghiên cứu định dạng PDF.
- **Tìm kiếm & RAG (Retrieval-Augmented Generation):** Lưu trữ vector (Vector store) với ChromaDB giúp truy xuất thông tin ngữ cảnh thông minh, chính xác từ bài báo.
- **Tóm tắt & Trích xuất:** Tự động tóm tắt nội dung chính, phương pháp nghiên cứu và kết luận.
- **AI Agent (Langchain/Langgraph):** Agent tự động quyết định cách xử lý các câu hỏi phức tạp liên quan đến tài liệu.
- **Giao diện & API:** Cung cấp API backend (FastAPI) và giao diện người dùng thân thiện (Streamlit).

## 🛠️ Công nghệ sử dụng

- **Ngôn ngữ:** Python >= 3.13
- **AI/LLM Framework:** Langchain, Langgraph, Langchain Google GenAI (Gemini)
- **Vector Database:** ChromaDB
- **Backend:** FastAPI, Uvicorn
- **Frontend:** Streamlit
- **Công cụ phân tích PDF:** PyMuPDF
- **Quản lý Package:** `uv`

## 🚀 Hướng dẫn cài đặt

### Yêu cầu hệ thống

- Python >= 3.13
- Package manager: `uv` (hoặc `pip`)

### 1. Clone repository

```bash
git clone https://github.com/your-username/research-paper-agent.git
cd research-paper-agent
```

### 2. Cài đặt các thư viện (Dependencies)

Dự án sử dụng `uv` để quản lý môi trường ảo và thư viện để tối ưu tốc độ:

```bash
# Tạo virtual environment và đồng bộ dependencies
uv sync
```

*Hoặc nếu bạn dùng `pip` (khi đã export requirements):*
```bash
python -m venv .venv
source .venv/bin/activate  # (Với Windows: .venv\Scripts\activate)
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường

Copy file `.env.example` thành `.env`:

```bash
cp .env.example .env
```

Mở file `.env` và điền các thông tin, đặc biệt là API key:
- `GOOGLE_API_KEY`: Lấy từ [Google AI Studio](https://aistudio.google.com/app/apikey)
- Tùy chỉnh các tham số chunking và ChromaDB nếu cần.

## 🎯 Hướng dẫn sử dụng

Dự án được thiết kế gồm Backend API (FastAPI) và Frontend UI (Streamlit).

### Chạy Backend API (FastAPI)

```bash
# Chạy server FastAPI tại http://localhost:8000
uv run uvicorn api.main:app --reload
```
Truy cập `http://localhost:8000/docs` để xem tài liệu API (Swagger UI).

### Chạy Giao diện người dùng (Streamlit)

Mở một terminal mới và chạy:

```bash
# Chạy ứng dụng Streamlit tại http://localhost:8501
uv run streamlit run frontend/app.py
```

## 📁 Cấu trúc thư mục (Project Structure)

```text
.
├── .agents/             # Cấu hình AI Assistant (Hướng dẫn code, prompt)
├── api/                 # FastAPI routes và controllers
├── config/              # Các file cấu hình hệ thống (settings.py)
├── core/                # Core logic, xử lý RAG, chunking
├── data/                # Thư mục chứa dữ liệu cục bộ (ChromaDB)
├── frontend/            # Giao diện người dùng bằng Streamlit
├── graph/               # Kiến trúc luồng của Langgraph
├── prompts/             # System prompts dành cho LLM và AI Agent
├── schemas/             # Pydantic schemas cho API request/response
├── services/            # Services kết nối bên ngoài (LLM, PDF parser, Search)
├── tests/               # Unit test 
├── .env.example         # Template chứa các biến môi trường
├── pyproject.toml       # Quản lý metadata và dependencies của dự án
└── uv.lock              # Lock file dependencies của uv
```

## 🤝 Đóng góp (Contributing)

Mọi sự đóng góp đều được chào đón! Vui lòng tham khảo file `AGENT.md` trong thư mục gốc để hiểu các nguyên tắc viết code (kiến trúc, coding standards, quy định về unit tests và Conventional Commits) trước khi tạo Pull Request.

## 📝 Giấy phép (License)

Dự án được phát triển dưới giấy phép MIT.
