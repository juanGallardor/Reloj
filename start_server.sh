#!/bin/bash
echo "Iniciando Clock App API..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000