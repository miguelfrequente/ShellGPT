echo "Checking Ollama installation"

if command -v ollama &> /dev/null; then
    echo "Ollama is installed"
    ollama --version
else
    echo "No Ollama installation found"
    exit 1
fi

echo "Creating virtual environment"

VENV_DIR="myenv"

if [ -d "myenv" ]; then
    echo "Virtual environment already exists"
else
    echo "Creating virtual environment"
    python3 -m venv "$VENV_DIR"

    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Check if Python is installed."
        exit 1
    fi

    echo "Virtual environment created successfully."
fi

if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "🔄 Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
else
    echo "Failed to activate virtual environment."
    exit 1
fi


echo "Executing building script"

pyinstaller --onefile --paths myenv/lib/python3.13/site-packages/ --clean llm_wrapper.py


echo ""
echo "Creating symbolic link"

sudo ln -s /Users/focustime/Documents/code/ShellGPT/dist/llm_wrapper /usr/local/bin/omni