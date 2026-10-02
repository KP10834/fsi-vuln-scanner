from __future__ import annotations

from engine.rule_engine import Rule

COMMON_RULES: list[Rule] = [
    Rule(
        "SEC-001", "CRITICAL",
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        "저장소 파일에 개인키가 포함되어 있습니다",
        "제거·교체 후 KMS/시크릿 매니저에서 로드하세요.",
        ("common",), True,
    ),
    Rule(
        "SEC-002", "HIGH",
        r"(?i)(aws_access_key_id|aws_secret_access_key|x-api-key|api[_-]?key)\s*[:=]\s*(['\"]?)[A-Za-z0-9/+=_-]{16,}",
        "자격증명으로 보이는 API 키가 하드코딩되어 있습니다",
        "환경변수/KMS 주입으로 바꾸고 소스에는 플레이스홀더만 두세요.",
        ("common",), False,
    ),
    Rule(
        "SEC-003", "MEDIUM",
        r"(?i)(client[_-]?secret|password|passwd|secret[_-]?key)\s*[:=]\s*(['\"])(?!\$\{|<|>|\*{3}|change[-_ ]?me|example|test-secret|your-)[^'\"]{8,}\2",
        "하드코딩된 비밀/비밀번호로 의심됩니다",
        "비운영 테스트 값인지 확인하고, 아니면 교체 후 시크릿 관리로 이전하세요.",
        ("common",), False,
    ),
    Rule(
        "SEC-004", "HIGH",
        r"(?i)(?:\b(?:log|logger)\s*\.(?:trace|debug|info|warn|error)|(?:print|println|console\.log)|fmt\.(?:Print|Printf|Println)|log\.(?:Print|Printf|Println))\s*\([^)]*(?:,|\+)\s*(?:password|passwd|client[_.]secret|authorization|bearer|access[_.]token|refresh[_.]token|private[_.]key|resident[_.]registration|rrn)\b",
        "민감정보가 로그에 기록될 수 있습니다",
        "식별자/단방향 지문만 로깅하고 자격증명·토큰·원본 PII는 남기지 마세요.",
        ("common",), False,
    ),
    Rule(
        "SEC-007", "MEDIUM",
        r"(?i)(allowedOrigins?\s*\(\s*['\"]\*['\"]\s*\)|Access-Control-Allow-Origin['\"]?\s*[:,]\s*['\"]\*)",
        "와일드카드 CORS origin이 발견되었습니다",
        "자격증명 사용 시 특히, 명시적 origin 허용목록을 사용하세요.",
        ("common",), False,
    ),
]
