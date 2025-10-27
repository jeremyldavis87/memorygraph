#!/bin/bash

# MemoryGraph Secrets Manager Script
# AWS Account: 969325212479

set -e

# Set AWS profile
export AWS_PROFILE=jeremy_personal_local
export AWS_REGION=us-east-1

# Function to display usage
usage() {
    echo "Usage: $0 [create|update|get|list|delete] [secret-name] [secret-value]"
    echo ""
    echo "Commands:"
    echo "  create <name> <value>  - Create a new secret"
    echo "  update <name> <value>  - Update an existing secret"
    echo "  get <name>             - Get secret value"
    echo "  list                   - List all memorygraph secrets"
    echo "  delete <name>          - Delete a secret"
    echo ""
    echo "Examples:"
    echo "  $0 create openai-api-key 'your-openai-key'"
    echo "  $0 update jwt-secret 'new-jwt-secret'"
    echo "  $0 get openai-api-key"
    echo "  $0 list"
    echo "  $0 delete openai-api-key"
}

# Function to create a secret
create_secret() {
    local name=$1
    local value=$2
    
    if [ -z "$name" ] || [ -z "$value" ]; then
        echo "Error: Secret name and value are required"
        usage
        exit 1
    fi
    
    echo "Creating secret: memorygraph/$name"
    aws secretsmanager create-secret \
        --name "memorygraph/$name" \
        --secret-string "$value" \
        --description "MemoryGraph $name secret"
    
    echo "✅ Secret created successfully"
}

# Function to update a secret
update_secret() {
    local name=$1
    local value=$2
    
    if [ -z "$name" ] || [ -z "$value" ]; then
        echo "Error: Secret name and value are required"
        usage
        exit 1
    fi
    
    echo "Updating secret: memorygraph/$name"
    aws secretsmanager update-secret \
        --secret-id "memorygraph/$name" \
        --secret-string "$value"
    
    echo "✅ Secret updated successfully"
}

# Function to get a secret value
get_secret() {
    local name=$1
    
    if [ -z "$name" ]; then
        echo "Error: Secret name is required"
        usage
        exit 1
    fi
    
    echo "Getting secret: memorygraph/$name"
    aws secretsmanager get-secret-value \
        --secret-id "memorygraph/$name" \
        --query SecretString \
        --output text
}

# Function to list all secrets
list_secrets() {
    echo "Listing all MemoryGraph secrets:"
    aws secretsmanager list-secrets \
        --query "SecretList[?contains(Name, 'memorygraph/')].{Name:Name,Description:Description,LastChangedDate:LastChangedDate}" \
        --output table
}

# Function to delete a secret
delete_secret() {
    local name=$1
    
    if [ -z "$name" ]; then
        echo "Error: Secret name is required"
        usage
        exit 1
    fi
    
    echo "Deleting secret: memorygraph/$name"
    read -p "Are you sure you want to delete this secret? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        aws secretsmanager delete-secret \
            --secret-id "memorygraph/$name" \
            --force-delete-without-recovery
        echo "✅ Secret deleted successfully"
    else
        echo "❌ Secret deletion cancelled"
    fi
}

# Main script logic
case "$1" in
    create)
        create_secret "$2" "$3"
        ;;
    update)
        update_secret "$2" "$3"
        ;;
    get)
        get_secret "$2"
        ;;
    list)
        list_secrets
        ;;
    delete)
        delete_secret "$2"
        ;;
    *)
        usage
        exit 1
        ;;
esac
