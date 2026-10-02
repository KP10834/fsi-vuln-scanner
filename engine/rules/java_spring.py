from __future__ import annotations

from engine.rule_engine import Rule

JAVA_RULES: list[Rule] = [
    Rule(
        "SEC-005", "HIGH",
        r"(?i)exposure\.include\s*[:=]\s*[\"']?\*|include:\s*[\"']?\*",
        "관리(Actuator) 엔드포인트가 전체(*) 노출로 설정되었습니다",
        "명시적 허용목록만 노출하고 네트워크 경계에서 보호하세요.",
        ("java_spring",), False,
    ),
    Rule(
        "SEC-006", "MEDIUM",
        r"(?i)include[-_.]stacktrace\s*[:=]\s*always",
        "HTTP 오류 응답에 스택트레이스가 항상 포함될 수 있습니다",
        "로컬 개발 외에는 스택트레이스 노출을 끄세요.",
        ("java_spring",), False,
    ),
    Rule(
        "JAVA-CORS-001", "MEDIUM",
        r"@CrossOrigin\s*\(\s*[\"']\*[\"']\s*\)",
        "@CrossOrigin 와일드카드가 사용되었습니다",
        "명시적 origin만 허용하세요.",
        ("java_spring",), False,
    ),
    Rule(
        "JAVA-SQL-001", "HIGH",
        r'(?i)"[^"]*\b(?:SELECT|INSERT|UPDATE|DELETE)\b[^"]*"\s*\+\s*[A-Za-z_]',
        "문자열 연결/Statement 기반 SQL 조립으로 인젝션 위험이 있습니다",
        "PreparedStatement와 바인딩 파라미터를 사용하세요.",
        ("java_spring",), False,
    ),
    Rule(
        "JAVA-HASH-001", "MEDIUM",
        r"getInstance\s*\(\s*[\"'](?:MD5|SHA-?1)[\"']\s*\)",
        "취약한 해시 알고리즘(MD5/SHA-1)이 사용되었습니다",
        "SHA-256 이상 또는 용도에 맞는 해시(비밀번호는 bcrypt/argon2)를 쓰세요.",
        ("java_spring",), False,
    ),
    Rule(
        "JAVA-CIPHER-001", "HIGH",
        r"getInstance\s*\(\s*[\"'][^\"']*/ECB/[^\"']*[\"']\s*\)",
        "ECB 블록 모드가 사용되었습니다",
        "GCM 등 인증 암호 모드를 사용하세요.",
        ("java_spring",), False,
    ),
    Rule(
        "JAVA-TLS-001", "HIGH",
        r"(?i)(TrustManager\s*\[\s*\]|checkServerTrusted\s*\([^)]*\)\s*\{\s*\}|setHostnameVerifier\s*\([^)]*ALLOW_ALL)",
        "TLS 인증서/호스트네임 검증이 무력화되었을 수 있습니다",
        "기본 검증을 유지하고 커스텀 TrustManager를 제거하세요.",
        ("java_spring",), False,
    ),
]
