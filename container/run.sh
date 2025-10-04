
#!/usr/bin/env bash
set -e

ARCHIVE_PATH=$(ls bomb.* 2>/dev/null | head -n 1)
LOG_FILE="/bomb/unpack.log"
REPORT_FILE="/bomb/report.json"

touch "$LOG_FILE"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

report() {
    local status="$1"
    local reason="$2"
    local size
    local duration="$(( $(date +%s) - $START_TIME ))"

    if [ -f "$ARCHIVE_PATH" ]; then
        size=$(stat --printf="%s" "$ARCHIVE_PATH")
    else
        size=0
    fi

    cat <<EOF > "$REPORT_FILE"
{
    "status": "$status",
    "reason": "$reason",
    "archive": "$(basename "$ARCHIVE_PATH")",
    "size_bytes": $size,
    "duration_seconds": $duration
}
EOF
}

START_TIME=$(date +%s)

log "👉 Распаковка архива: $ARCHIVE_PATH"

if [ ! -f "$ARCHIVE_PATH" ]; then
    log "❌ Файл архива не найден!"
    report "failed" "archive not found"
    exit 1
fi

EXT="${ARCHIVE_PATH##*.}"
log "🧬 Расширение: .$EXT"


extract() {
    case "$EXT" in
        zip)
            unzip "$ARCHIVE_PATH"
            ;;
        rar)
            unrar x "$ARCHIVE_PATH"
            ;;
        7z)
            7z x "$ARCHIVE_PATH"
            ;;
        tar)
            tar -xf "$ARCHIVE_PATH"
            ;;
        gz)
            tar -xzf "$ARCHIVE_PATH"
            ;;
        bz2)
            tar -xjf "$ARCHIVE_PATH"
            ;;
        *)
            log "❌ Неизвестный формат архива: .$EXT"
            report "failed" "unsupported format"
            exit 1
            ;;
    esac
}

# Ловим ошибки распаковки
if ! extract; then
    log "💥 Ошибка при распаковке"
    report "failed" "extract error"
    exit 1
fi

# Защита от рекурсии: ищем архивы внутри
RECURSION_FOUND=$(find . -type f \( -name "*.zip" -o -name "*.rar" -o -name "*.7z" -o -name "*.tar" -o -name "*.gz" -o -name "*.bz2" \) | wc -l)

if [ "$RECURSION_FOUND" -gt 10 ]; then
    log "🛑 Обнаружено вложенных архивов: $RECURSION_FOUND — считаем это атакой"
    report "failed" "recursive archive detected"
    exit 1
fi

log "✅ Архив успешно распакован"
report "success" "ok"