# ClippyIO 
Distributed Smart Video Processing Tool for Long Form Content into Shorts

## Workflow Overview

```
User
  |
  |  HTTPS upload
  v
Frontend (Next.js / Vercel)
  |
  |  POST /upload
  v
Nginx (Reverse Proxy + TLS)
  |
  |  Proxy to API
  v
Backend API (FastAPI)
  |
  |  Upload raw video
  |  Enqueue job
  v
Amazon S3  <--------->  Amazon SQS
                          |
                          |  Long polling
                          v
                   GPU Worker (EC2 g4dn)
                          |
                          |  Transcribe / Process / Cut
                          v
                      Amazon S3 (Results)
                          |
                          |  Status + metadata
                          v
Frontend polling → User receives clips
```

---

## Backend API

**Stack**
- Python 3.11  
- FastAPI (ASGI)  
- Uvicorn  
- Docker  
- OpenAI API  
- Whisper / WhisperFlow  
- FFmpeg  
- boto3 (AWS SDK)

**Consists of**
- Stateless REST endpoints  
- Multipart video ingestion  
- S3 upload orchestration  
- SQS job dispatch  
- Job status and result retrieval  
- OpenAPI / Swagger documentation  

**Design**
- Non-blocking request lifecycle  
- No heavy compute on API layer  
- Clean separation between I/O and processing  

---

## Worker (Async + GPU)

**Stack**
- Python 3.11  
- Docker (CUDA-enabled)  
- NVIDIA CUDA (T4)  
- PyTorch (GPU inference)  
- Whisper  
- FFmpeg  
- Amazon SQS  
- Amazon S3  

**Consists of**
- Long-polling SQS consumer  
- Per-job isolated temp workspace  
- GPU-accelerated speech-to-text  
- Clip boundary detection  
- Video cutting via FFmpeg  
- Caption and summary generation  
- Result uploads and status tracking  

**Design**
- GPU-first compute node  
- Decoupled from API  
- Fault-isolated per job  
- Horizontally scalable  

---

## Frontend

**Stack**
- Next.js  
- React  
- TypeScript  
- Tailwind CSS  
- Vercel (hosting + CI/CD)  

**Consists of**
- Client-side upload handling  
- API integration via fetch  
- Job status polling  
- Stateless UI design  

**Design**
- Lightweight, serverless deployment  
- No backend coupling  
- Environment-based API configuration  

---

## Networking & Security

**Stack**
- Nginx  
- HTTPS (TLS)  
- Certbot  
- Let’s Encrypt  
- DNS-based routing  

**Consists of**
- Reverse proxying to FastAPI  
- TLS termination at edge  
- HTTP → HTTPS redirection  
- Centralized CORS handling  
- Preflight request support  

**Design**
- Encrypted traffic end-to-end  
- Transport concerns separated from app logic  
- Production-grade network hardening  

---

## AWS Infrastructure

**Services**
- **EC2**
  - CPU instance: backend API  
  - GPU instance (g4dn.xlarge): worker  
- **S3**
  - Raw uploads  
  - Processed clips  
  - Status and results metadata  
- **SQS**
  - Asynchronous job orchestration 

**Design**
- Decoupled compute layers  
- Asynchronous scaling model  
- Cost-aware infrastructure separation  

---

## Architectural Summary

- Fully asynchronous processing pipeline  
- GPU-accelerated ML workloads  
- Containerized services  
- Cloud-native AWS architecture  
- Secure, HTTPS-first networking  
- Designed for scalability and production use  
