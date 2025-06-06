#!/bin/bash

# ===============================================
# Script de automação ETL Docker + PostgreSQL
# Inicia containers, aplica views e fornece menu
# Compatível com Linux, macOS, Git Bash e WSL
# ===============================================

DOCKER_SERVICE="beanalytic-db-1"
DB_CHECK_CMD="docker exec $DOCKER_SERVICE pg_isready -U postgres -d beanalytic"

detect_os() {
    unameOut="$(uname -s)"
    case "${unameOut}" in
        Linux*)     OS=Linux ;;
        Darwin*)    OS=Mac ;;
        CYGWIN*|MINGW*|MSYS*) OS=Windows ;;
        *)          OS="UNKNOWN:${unameOut}" ;;
    esac
    echo "[INFO] Sistema operacional detectado: $OS"
}

start_docker() {
    echo "[INFO] Iniciando Docker Compose..."

    case "$OS" in
        Linux)
            gnome-terminal -- bash -c "docker compose up --build; exec bash" 2>/dev/null || x-terminal-emulator -e "docker compose up --build"
            ;;
        Mac)
            osascript <<EOF
tell application "Terminal"
    do script "cd \"$(pwd)\" && docker compose up --build"
end tell
EOF
            ;;
        Windows)
            start "" cmd /c "docker compose up --build"
            ;;
        *)
            echo "[ERRO] SO não suportado para terminal paralelo."
            ;;
    esac
}

aguardar_inicializacao() {
    echo "[INFO] Aguardando criação do banco..."
    sleep 30

    if ! $DB_CHECK_CMD > /dev/null 2>&1; then
        echo "[ERRO] Servidor ainda não disponível."
        exit 1
    fi
}

menu() {
    echo ""
    echo "======= MENU DE OPÇÕES ======="
    echo "1) Acessar terminal do banco (psql)"
    echo "2) Executar views.sql"
    echo "3) Ver dados da view vw_variacao_ida"
    echo "4) Derrubar containers e apagar banco"
    echo "5) Sair"
    echo "==============================="
    read -p "Digite um número dentre as opções acima: " opcao

    case $opcao in
        1)
            docker exec -it $DOCKER_SERVICE psql -U postgres -d beanalytic
            ;;
        2)
            docker exec -i $DOCKER_SERVICE psql -U postgres -d beanalytic < postgres/views.sql \
            && echo "[INFO] Views executadas."
            ;;
        3)
            docker exec -it $DOCKER_SERVICE psql -U postgres -d beanalytic -c "SELECT * FROM vw_variacao_ida LIMIT 10;"
            ;;
        4)
            echo "[INFO] Finalizando containers e removendo volumes..."
            docker compose down -v
            ;;
        5)
            echo "[INFO] Encerrando e removendo containers..."
            docker compose down -v
            exit 0
            ;;
        *)
            echo "[ERRO] Opção inválida."
            ;;
    esac
}

main() {
    detect_os
    start_docker
    aguardar_inicializacao

    while true; do
        menu
        read -p "Pressione ENTER para continuar..."
    done
}

main
