
# GPU Docker Worker Quick Start Guide

This guide lets **anyone with an NVIDIA GPU** spin up your Docker worker reliably.
Works for **local machines, servers, or cloud GPUs**.

---

## 0. Prerequisites
- NVIDIA GPU
- NVIDIA driver installed
- Docker installed
- NVIDIA Container Toolkit installed

---

## 1. Verify GPU on Host
```bash
nvidia-smi
```
If this prints a table → GPU driver is working.

---

## 2. Verify Docker GPU Access
```bash
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```
If this prints the same GPU table → Docker + GPU are wired correctly.

---

## 3. Build the Worker Image
From the `workers/` directory:
```bash
docker build -t clippyio-worker .
```

---

## 4. Run the Worker (GPU Enabled, Persistent)
```bash
docker run -d   --gpus all   --shm-size=2g   --restart unless-stopped   --env-file .env  --name clippyio-worker  clippyio-worker
```

---

## 5. Verify Worker Is Running
```bash
docker ps
```

View logs:
```bash
docker logs -f clippyio-worker
```

---

## 6. Stop / Restart Worker
```bash
docker stop clippyio-worker
docker start clippyio-worker
```

---

## 7. Multiple Workers on One Machine
Run multiple workers by changing the container name:
```bash
docker run -d   --gpus all   --shm-size=2g   --restart unless-stopped   --name clippyio-worker-2   -e API_URL=http://host.docker.internal:8000   clippyio-worker
```

---

## 8. Optional: Lock Kernel (Debian/Ubuntu)
Prevents GPU breakage due to kernel upgrades:
```bash
sudo apt-mark hold linux-image-amd64 linux-headers-amd64
```

---

## One-Line GPU Sanity Check
```bash
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

If this works, **everything downstream will work**.

---

## Notes
- `--shm-size=2g` is important for PyTorch / CUDA workloads
- `--restart unless-stopped` ensures persistence across reboots
- Use `host.docker.internal` to reach services running on the host

---

