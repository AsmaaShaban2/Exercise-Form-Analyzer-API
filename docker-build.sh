#!/bin/bash

# Docker build and run script for Exercise Analysis API

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="exercise-analysis-api"
CONTAINER_NAME="exercise-analysis-container"
PORT=5000

echo -e "${BLUE}=== Exercise Analysis API Docker Build Script ===${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed and running
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_status "Docker is installed and running."
}

# Build Docker image
build_image() {
    print_status "Building Docker image: $IMAGE_NAME"
    
    # Remove existing image if it exists
    if docker image inspect $IMAGE_NAME &> /dev/null; then
        print_warning "Removing existing image: $IMAGE_NAME"
        docker rmi $IMAGE_NAME
    fi
    
    # Build the image
    docker build -t $IMAGE_NAME .
    
    if [ $? -eq 0 ]; then
        print_status "Docker image built successfully!"
    else
        print_error "Failed to build Docker image."
        exit 1
    fi
}

# Stop and remove existing container
cleanup_container() {
    if docker ps -a --format 'table {{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
        print_warning "Stopping and removing existing container: $CONTAINER_NAME"
        docker stop $CONTAINER_NAME &> /dev/null || true
        docker rm $CONTAINER_NAME &> /dev/null || true
    fi
}

# Run Docker container
run_container() {
    print_status "Starting Docker container: $CONTAINER_NAME"
    
    # Create necessary directories on host
    mkdir -p uploads reports logs
    
    # Run the container
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:5000 \
        -v "$(pwd)/uploads:/app/uploads" \
        -v "$(pwd)/reports:/app/reports" \
        -v "$(pwd)/logs:/app/logs" \
        -e FLASK_ENV=production \
        $IMAGE_NAME
    
    if [ $? -eq 0 ]; then
        print_status "Container started successfully!"
        print_status "API is available at: http://localhost:$PORT"
        print_status "Health check: http://localhost:$PORT/health"
    else
        print_error "Failed to start container."
        exit 1
    fi
}

# Show container logs
show_logs() {
    print_status "Container logs:"
    docker logs $CONTAINER_NAME
}

# Show container status
show_status() {
    print_status "Container status:"
    docker ps --filter "name=$CONTAINER_NAME"
}

# Main execution
main() {
    case "${1:-build}" in
        "build")
            check_docker
            build_image
            ;;
        "run")
            check_docker
            cleanup_container
            run_container
            ;;
        "build-and-run")
            check_docker
            build_image
            cleanup_container
            run_container
            ;;
        "stop")
            print_status "Stopping container: $CONTAINER_NAME"
            docker stop $CONTAINER_NAME
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "clean")
            print_status "Cleaning up containers and images..."
            cleanup_container
            if docker image inspect $IMAGE_NAME &> /dev/null; then
                docker rmi $IMAGE_NAME
            fi
            print_status "Cleanup complete."
            ;;
        "help")
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  build         Build Docker image only"
            echo "  run           Run container (assumes image exists)"
            echo "  build-and-run Build image and run container (default)"
            echo "  stop          Stop running container"
            echo "  logs          Show container logs"
            echo "  status        Show container status"
            echo "  clean         Remove container and image"
            echo "  help          Show this help message"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for usage information."
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
