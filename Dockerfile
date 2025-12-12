# Use a python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set the working directory to /app
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy the lockfile and pyproject.toml first to leverage cache
COPY uv.lock pyproject.toml /app/

# Install dependencies using uv
# --frozen ensures we use exact versions from uv.lock
# --no-dev excludes development dependencies if any (though usually we might want them for certain dev setups, for "others to use" we assume prod use case, but pyproject.toml structure here is simple so we just sync)
# --no-install-project skips installing the project itself as a package (unless it is one), focused on deps first
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application code
COPY . /app/

# Install the project itself (if needed) or just ensure environment is ready
RUN uv sync --frozen --no-dev

# Expose port 8501 for Streamlit
EXPOSE 8501

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"

RUN chmod 777 ./

# Run the application
CMD ["uv", "run", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
