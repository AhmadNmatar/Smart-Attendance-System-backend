## Quick start
1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate    # Windows 
   ```
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   fastapi run app/main.py
   ```

After running the app, FastAPI automatically generates interactive documentation where you can test all endpoints and see required data.

Swagger UI:
👉 http://0.0.0.0:8000/docs