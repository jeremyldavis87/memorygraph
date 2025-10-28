#!/bin/bash

# Podman Migration Test Script
# This script tests the Podman migration for MemoryGraph

set -e

echo "🧪 Testing Podman Migration for MemoryGraph..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Test 1: Check if Podman is installed
test_podman_installation() {
    print_status "Testing Podman installation..."
    
    if command -v podman &> /dev/null; then
        PODMAN_VERSION=$(podman --version)
        print_status "✅ Podman is installed: $PODMAN_VERSION"
    else
        print_error "❌ Podman is not installed"
        print_warning "Install with: sudo apt install podman"
        return 1
    fi
}

# Test 2: Check if Podman Compose is installed
test_podman_compose_installation() {
    print_status "Testing Podman Compose installation..."
    
    if command -v podman-compose &> /dev/null; then
        PODMAN_COMPOSE_VERSION=$(podman-compose --version)
        print_status "✅ Podman Compose is installed: $PODMAN_COMPOSE_VERSION"
    else
        print_error "❌ Podman Compose is not installed"
        print_warning "Install with: pip install podman-compose"
        return 1
    fi
}

# Test 3: Check if Podman is running
test_podman_running() {
    print_status "Testing if Podman is running..."
    
    if podman info > /dev/null 2>&1; then
        print_status "✅ Podman is running"
    else
        print_error "❌ Podman is not running"
        print_warning "Start Podman with: podman system service --time=0 &"
        return 1
    fi
}

# Test 4: Validate compose files
test_compose_files() {
    print_status "Testing compose files..."
    
    # Check if podman-compose files exist
    if [ -f "podman-compose.yml" ]; then
        print_status "✅ podman-compose.yml exists"
    else
        print_error "❌ podman-compose.yml not found"
        return 1
    fi
    
    if [ -f "podman-compose.local.yml" ]; then
        print_status "✅ podman-compose.local.yml exists"
    else
        print_error "❌ podman-compose.local.yml not found"
        return 1
    fi
    
    # Validate compose file syntax
    if podman-compose -f podman-compose.yml config > /dev/null 2>&1; then
        print_status "✅ podman-compose.yml syntax is valid"
    else
        print_error "❌ podman-compose.yml has syntax errors"
        return 1
    fi
    
    if podman-compose -f podman-compose.local.yml config > /dev/null 2>&1; then
        print_status "✅ podman-compose.local.yml syntax is valid"
    else
        print_error "❌ podman-compose.local.yml has syntax errors"
        return 1
    fi
}

# Test 5: Test image building
test_image_building() {
    print_status "Testing image building..."
    
    # Test backend image build
    if podman build -t memorygraph-backend-test ./backend > /dev/null 2>&1; then
        print_status "✅ Backend image builds successfully"
        # Clean up test image
        podman rmi memorygraph-backend-test > /dev/null 2>&1 || true
    else
        print_error "❌ Backend image build failed"
        return 1
    fi
    
    # Test frontend image build
    if podman build -t memorygraph-frontend-test ./frontend > /dev/null 2>&1; then
        print_status "✅ Frontend image builds successfully"
        # Clean up test image
        podman rmi memorygraph-frontend-test > /dev/null 2>&1 || true
    else
        print_error "❌ Frontend image build failed"
        return 1
    fi
}

# Test 6: Test service startup (dry run)
test_service_startup() {
    print_status "Testing service startup (dry run)..."
    
    # Test if services can be started (without actually starting them)
    if podman-compose -f podman-compose.local.yml config > /dev/null 2>&1; then
        print_status "✅ Services can be configured for startup"
    else
        print_error "❌ Service configuration failed"
        return 1
    fi
}

# Test 7: Check script updates
test_script_updates() {
    print_status "Testing script updates..."
    
    # Check if start.sh uses podman-compose
    if grep -q "podman-compose" start.sh; then
        print_status "✅ start.sh uses podman-compose"
    else
        print_error "❌ start.sh still uses docker-compose"
        return 1
    fi
    
    # Check if stop.sh uses podman-compose
    if grep -q "podman-compose" stop.sh; then
        print_status "✅ stop.sh uses podman-compose"
    else
        print_error "❌ stop.sh still uses docker-compose"
        return 1
    fi
    
    # Check if Makefile uses podman-compose
    if grep -q "podman-compose" Makefile; then
        print_status "✅ Makefile uses podman-compose"
    else
        print_error "❌ Makefile still uses docker-compose"
        return 1
    fi
}

# Test 8: Check documentation updates
test_documentation_updates() {
    print_status "Testing documentation updates..."
    
    # Check if README mentions Podman
    if grep -q "Podman" README.md; then
        print_status "✅ README.md mentions Podman"
    else
        print_error "❌ README.md doesn't mention Podman"
        return 1
    fi
    
    # Check if DEVELOPMENT.md mentions Podman
    if grep -q "Podman" DEVELOPMENT.md; then
        print_status "✅ DEVELOPMENT.md mentions Podman"
    else
        print_error "❌ DEVELOPMENT.md doesn't mention Podman"
        return 1
    fi
}

# Main test function
main() {
    print_status "Starting Podman migration tests..."
    echo ""
    
    local tests_passed=0
    local total_tests=8
    
    # Run all tests
    test_podman_installation && ((tests_passed++))
    test_podman_compose_installation && ((tests_passed++))
    test_podman_running && ((tests_passed++))
    test_compose_files && ((tests_passed++))
    test_image_building && ((tests_passed++))
    test_service_startup && ((tests_passed++))
    test_script_updates && ((tests_passed++))
    test_documentation_updates && ((tests_passed++))
    
    echo ""
    print_status "Test Results: $tests_passed/$total_tests tests passed"
    
    if [ $tests_passed -eq $total_tests ]; then
        print_status "🎉 All tests passed! Podman migration is successful."
        echo ""
        print_status "Next steps:"
        echo "1. Run './start.sh' to start the development environment"
        echo "2. Test the application at http://localhost:3001"
        echo "3. Check logs with 'podman-compose -f podman-compose.yml logs -f'"
    else
        print_error "❌ Some tests failed. Please fix the issues before proceeding."
        echo ""
        print_warning "Common fixes:"
        echo "1. Install Podman: sudo apt install podman"
        echo "2. Install Podman Compose: pip install podman-compose"
        echo "3. Start Podman: podman system service --time=0 &"
        echo "4. Check file permissions and syntax"
    fi
}

# Run main function
main "$@"
