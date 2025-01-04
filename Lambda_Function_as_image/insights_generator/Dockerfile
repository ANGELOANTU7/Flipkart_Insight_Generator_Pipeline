# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV MPLCONFIGDIR="/tmp/matplotlib"
ENV YOLO_CONFIG_DIR="/tmp/ultralytics"
# Force CPU only mode
ENV CUDA_VISIBLE_DEVICES=""
# Optimize Python startup
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Update package lists and install Python 3.10 and other dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3.10-dev \
    gcc \
    g++ \
    make \
    libgl1-mesa-dev \
    libglib2.0-0 \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt ./


# Copy the model and function code
COPY submodules ./submodules
COPY .env ./
COPY lambda_function.py ./


# Add these to your Dockerfile before the final CMD
RUN pip3 install -r requirements.txt
RUN pip3 install  awslambdaric

# If you want to use the Lambda Runtime Interface Emulator
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
RUN chmod 755 /usr/bin/aws-lambda-rie

ENTRYPOINT [ "/usr/bin/python3", "-m", "awslambdaric" ]
CMD [ "lambda_function.lambda_handler" ]