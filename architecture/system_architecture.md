# System Architecture

## Overview

Enterprise AI Knowledge Assistant is a multi-tenant RAG (Retrieval-Augmented
Generation) platform allowing organizations to upload documents and query
them via AI, with mandatory source citations.

## Known Deployment Considerations

- `chroma-hnswlib` (a ChromaDB dependency) requires C++ compilation during
  install. On resource-constrained instances (e.g., AWS t2.micro with 1GB
  RAM), this compilation can be slow or fail due to memory limits. For
  production deployment, either:
  - use a slightly larger instance (t3.small or above), or
  - add swap space to the instance before building:
```
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
```