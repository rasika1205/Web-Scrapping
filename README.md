![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Build Passing](https://img.shields.io/badge/build-passing-brightgreen.svg)
![License](https://img.shields.io/badge/license-proprietary-lightgrey.svg)

---

# Web Scrapping Project

**Overview:**  
This project demonstrates a complete pipeline from **web scraping HTML pages**, saving them as static files, then using those scraped pages in a semantic search and question-answering web application.  
**The key highlight is how scraped content is transformed and leveraged:**  
- **Web pages are scraped and downloaded to a `static` folder.**
- **The app then processes these files—extracting, cleaning, converting to PDF, and enabling powerful search and Q&A over the collected data.**

---

## Table of Contents

- [Demo](#demo)
- [Features](#features)
- [How It Works](#how-it-works)
  - [Web Scraping Process (Highlighted)](#web-scraping-process-highlighted)
  - [What Happens with the Scraped Pages](#what-happens-with-the-scraped-pages)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [Future Enchancements](#future-enhancements)
- [License](#license)

---

## Demo

<img width="1596" height="761" alt="Screenshot 2025-07-14 204933" src="https://github.com/user-attachments/assets/f2cada91-a378-42ba-b4c2-d0fdad6e3d86" />


---

## Features

- **Automated Web Scraping**: Fetches and stores HTML pages from target URLs.
- **Static File Storage**: Scraped HTML and generated PDF files are saved in the `static` directory.
- **Content Processing**: Extracts, cleans, and converts web content to PDF for downstream use.
- **Semantic Search & Q&A**: Indexes documents for fast search and retrieval; users can ask questions about the content.
- Modular and extensible pipeline.

---

## How It Works

### Web Scraping Process (Highlighted)

**Web scraping is at the core of this project!**  
- Python scripts fetch specified HTML pages from the web.
- Each page is saved as an HTML file in the `static` directory.
- The scraped HTML is parsed, cleaned, and then **converted to PDF files**, also stored in `static`.

**Sample snippet:**
```python
import requests

url = "https://example.com"
response = requests.get(url)
with open("static/example.html", "w", encoding="utf-8") as file:
    file.write(response.text)
# parse, clean, and convert to PDF using functions in app.py
```

---

### What Happens with the Scraped Pages

After scraping and converting HTML to PDF, the app leverages these files for semantic search and question answering:

- **Loading Documents**: All PDFs in `static` are loaded automatically.
- **Text Splitting**: PDFs are split into smaller text chunks for processing.
- **Embedding & Indexing**: Chunks are embedded using a transformer model and indexed with FAISS for fast semantic retrieval.
- **Retrieval-Augmented QA**: Users can ask questions; relevant PDF chunks are surfaced and passed to a language model (e.g., Gemini) for concise, context-aware answers, including source references.
- **Conversational Memory**: The app maintains chat history for context-aware interactions.

**Workflow excerpt (`app.py`):**
```python
documents = get_document_loader()
chunks = get_text_chunks(documents)
db = FAISS.from_documents(chunks, embeddings)  # or load from disk
retriever = db.as_retriever()
chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
# Handles user Q&A over the content
```

---

## Setup & Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/rasika1205/Web-Scrapping.git
    cd Web-Scrapping
    ```
2. (Optional) Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Run the application:
    ```bash
    python app.py
    ```

---

## Usage

- Launch the app and open your browser to the local address given in the terminal.
- The web interface allows you to ask questions about the scraped and processed content.
- To expand coverage, add more scraping targets or enhance the processing logic.

---

## Future Enhancements

1. **Support for More Websites**  
   Extend the scraper’s capabilities to handle a wider variety of websites, including those with advanced anti-bot measures or dynamic content loaded via JavaScript.

2. **User-Friendly Interface**  
   Develop a graphical user interface (GUI) or a web dashboard to make the tool accessible to users without coding experience.

3. **Scheduler and Automation**  
   Implement scheduling features to enable automated, periodic scraping tasks with configurable intervals.

4. **Data Export Options**  
   Add support for exporting scraped data in various formats such as CSV, Excel, JSON, or databases.

5. **Error Handling and Logging**  
   Enhance error handling to gracefully manage network issues, website changes, and provide detailed logs for easier debugging.

6. **Scalability and Performance**  
   Optimize the code for faster scraping and introduce support for parallel or distributed scraping to handle large-scale data extraction.

7. **Data Cleaning and Analysis Tools**  
   Integrate basic data cleaning and analysis features to provide insights and visualizations directly in the application.

8. **Authentication and Proxies**  
   Allow the use of authenticated sessions and proxy rotation to avoid IP bans and access restricted content.

9. **Notification System**  
   Implement email or push notifications to inform users about the completion of scraping jobs or encountered errors.

10. **API Integration**  
    Offer an API for programmatic access so other applications can trigger scraping and retrieve results.

---
## License

This project is **proprietary** and protected by copyright © 2025 Rasika Gautam.

You are welcome to view the code for educational or evaluation purposes (e.g., portfolio review by recruiters).  
However, you may **not copy, modify, redistribute, or claim this project as your own** under any circumstances — including in interviews or job applications — without written permission.

---

## 🧑‍💻 Author

**Rasika Gautam**
*Data Science & AI Enthusiast* | B.Tech MAC, NSUT
[GitHub](https://github.com/rasika1205)


**_Summary: This project’s strength is its end-to-end pipeline: web pages are scraped, saved, processed, and transformed into a searchable, answerable knowledge base—enabling powerful Q&A on your own curated data!_**

---
