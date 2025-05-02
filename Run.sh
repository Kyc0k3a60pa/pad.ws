#!/bin/bash

# Функция для проверки и записи переменных в .env
set_env_var() {
    local var_name=$1
    local prompt=$2
    local default_value=$3

    current_value=$(grep -E "^$var_name=" .env | cut -d '=' -f2-)
    if [[ -n "$current_value" ]]; then
        read -p "$var_name уже установлено в '$current_value'. Хотите изменить? (y/n) " change
        if [[ "$change" != "y" ]]; then
            return
        fi
    fi

    read -p "$prompt " value
    if [[ -z "$value" && -n "$default_value" ]]; then
        value=$default_value
    fi

    if [[ -n "$value" ]]; then
        if grep -qE "^$var_name=" .env; then
            sed -i "s/^$var_name=.*/$var_name=$value/" .env
        else
            echo "$var_name=$value" >> .env
        fi
    fi
}

# Выводим информационное сообщение
echo "This script helps to easily deploy the software on a remote server or locally (for local deployment use 'localhost' as domain name)."
echo "You can only use this script if you understand how it works and agree to take responsibility for the security of the software."
echo ""

# Запрашиваем согласие с условиями
read -p "Do you agree to the terms of using this script? (y/n) " agree
if [[ "$agree" != "y" ]]; then
    echo "Script execution aborted."
    exit 1
fi

# Копируем шаблон .env, если его нет
if [[ ! -f ".env" ]]; then
    cp .env.template .env
    echo "Created .env file from template."
fi

# Запрашиваем доменное имя
current_domain=$(grep -E "^DOMAIN_RS=" .env | cut -d '=' -f2-)
if [[ -n "$current_domain" ]]; then
    read -p "DOMAIN_RS is already set to '$current_domain'. Do you want to change it? (y/n) " change_domain
    if [[ "$change_domain" == "y" ]]; then
        read -p "Enter domain name bound to server address: " domain
        if [[ -n "$domain" ]]; then
            sed -i "s/^DOMAIN_RS=.*/DOMAIN_RS=$domain/" .env
        fi
    fi
else
    read -p "Enter domain name bound to server address: " domain
    if [[ -n "$domain" ]]; then
        echo "DOMAIN_RS=$domain" >> .env
    fi
fi

# Получаем и записываем DOCKER_GROUP_ID
docker_group_id=$(getent group docker | cut -d: -f3)
if grep -qE "^DOCKER_GROUP_ID=" .env; then
    sed -i "s/^DOCKER_GROUP_ID=.*/DOCKER_GROUP_ID=$docker_group_id/" .env
else
    echo "DOCKER_GROUP_ID=$docker_group_id" >> .env
fi

# Запускаем контейнеры
echo "Starting postgres container..."
docker compose up -d postgres
if [[ $(docker ps -q -f name=postgres) ]]; then
    echo "Postgres container started successfully."
else
    echo "Failed to start postgres container."
    exit 1
fi

echo "Starting redis container..."
docker compose up -d redis
if [[ $(docker ps -q -f name=redis) ]]; then
    echo "Redis container started successfully."
else
    echo "Failed to start redis container."
    exit 1
fi

echo "Starting keycloak container..."
docker compose up -d keycloak
if [[ $(docker ps -q -f name=keycloak) ]]; then
    echo "Keycloak container started successfully."
else
    echo "Failed to start keycloak container."
    exit 1
fi

# Получаем KEYCLOAK_URL из .env
keycloak_url=$(grep -E "^KEYCLOAK_URL=" .env | cut -d '=' -f2-)
echo ""
echo "Now you need to configure Keycloak:"
echo "1. Open Keycloak admin interface: $keycloak_url"
echo "2. Follow the instructions from point 4 of the README: https://github.com/pad-ws/pad.ws"
echo ""

# Запрашиваем параметры Keycloak
set_env_var "OIDC_REALM" "Enter OIDC_REALM:"
set_env_var "OIDC_CLIENT_ID" "Enter OIDC_CLIENT_ID:"
set_env_var "OIDC_CLIENT_SECRET" "Enter OIDC_CLIENT_SECRET:"

# Запускаем coder
echo "Starting coder container..."
docker compose up -d coder
if [[ $(docker ps -q -f name=coder) ]]; then
    echo "Coder container started successfully."
else
    echo "Failed to start coder container."
    exit 1
fi

# Получаем CODER_URL из .env
coder_url=$(grep -E "^CODER_URL=" .env | cut -d '=' -f2-)
echo ""
echo "Now you need to configure Coder:"
echo "1. Open Coder interface: $coder_url"
echo "2. Follow the instructions from point 5 of the README: https://github.com/pad-ws/pad.ws"
echo ""

# Запрашиваем параметры Coder
set_env_var "CODER_API_KEY" "Enter CODER_API_KEY:"
set_env_var "CODER_TEMPLATE_ID" "Enter CODER_TEMPLATE_ID:"
set_env_var "CODER_DEFAULT_ORGANIZATION" "Enter CODER_DEFAULT_ORGANIZATION:"

# Запускаем pad
echo "Starting pad container..."
docker compose up -d pad
if [[ $(docker ps -q -f name=pad) ]]; then
    echo "Pad container started successfully."
    echo "Deployment completed!"
else
    echo "Failed to start pad container."
    exit 1
fi