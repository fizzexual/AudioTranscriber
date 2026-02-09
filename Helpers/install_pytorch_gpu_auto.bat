@echo off
echo Installing PyTorch with CUDA Support for RTX 4060...
echo.

echo Step 1: Uninstalling CPU-only PyTorch...
pip uninstall -y torch torchvision torchaudio

echo.
echo Step 2: Installing PyTorch with CUDA 12.1...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo.
echo Step 3: Verifying GPU support...
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA Available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

echo.
echo Done! If CUDA Available = True, GPU is ready!
