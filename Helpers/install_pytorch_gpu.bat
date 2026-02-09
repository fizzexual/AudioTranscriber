@echo off
echo ========================================
echo Installing PyTorch with CUDA Support
echo ========================================
echo.
echo Your GPU: NVIDIA GeForce RTX 4060 Laptop
echo This will enable GPU acceleration for Whisper!
echo.
pause

echo Uninstalling CPU-only PyTorch...
pip uninstall -y torch torchvision torchaudio

echo.
echo Installing PyTorch with CUDA 12.1 support...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo.
echo ========================================
echo Verifying installation...
echo ========================================
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('GPU Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

echo.
echo ========================================
echo Installation complete!
echo ========================================
pause
