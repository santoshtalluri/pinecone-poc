# rag_with_url
# 🚀 RAG-Based AI System with Query & URL-Based Updates

The **RAG-Based AI System** allows users to create, query, and update a **Retrieval-Augmented Generation (RAG) model**. It processes **PDFs, TXT files, and web URLs** to create a knowledge base and offers a CLI and **API-based interface** for querying and updating the model.

---

## 📘 **Table of Contents**
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [System Requirements](#system-requirements)
4. [Installation](#installation)
5. [Usage](#usage)
6. [API Documentation](#api-documentation)
7. [File Structure](#file-structure)
8. [How to Run](#how-to-run)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)

---

## 📘 **Project Overview**
The RAG system allows for interactive data processing from **PDF, TXT files, and URLs** to create a **centralized RAG-based knowledge system**. Users can query the system through a **CLI** or **API**.

**Why use this?**
- Consolidate multiple documents and URL content into a single **vectorized knowledge system**.
- Query data from multiple file types using **natural language**.
- Update the knowledge base dynamically using API endpoints.

---

## 🔥 **Features**
- **RAG System Creation** from PDF, TXT, and URL files.
- **Dynamic RAG Initialization** from files or uploaded content.
- **Interactive CLI** to query, update, and exit.
- **API Endpoints** to query, update, and check RAG system status.
- **File-Based RAG Creation** using PDF/TXT files in a pre-configured directory.
- **Real-Time Logging** for debugging.
- **Scalability** for large PDFs, TXT files, and URL content.
- **Spinner Animations** for a better CLI experience.
- **Customizable Configuration** using `.env` or `config.py`.

---

## 💻 **System Requirements**
- **Python 3.11+**
- **Flask** - Web server for API routes
- **LangChain** - For RAG system creation
- **FAISS** - For vector storage
- **PyPDF2** - For extracting content from PDFs
- **dotenv** - To manage environment variables
- **requests** - For URL requests
- **halo** - Spinner animations

---

## 🔧 **Installation**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/rag_with_url_project.git
   cd rag_with_url_project

   