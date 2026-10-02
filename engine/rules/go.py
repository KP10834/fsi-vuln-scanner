from __future__ import annotations

from engine.rule_engine import Rule

GO_RULES: list[Rule] = [
    Rule(
        "GO-SQL-001", "HIGH",
        r"fmt\.Sprintf\s*\(\s*[\"'](?i:[^\"']*\b(?:SELECT|INSERT|UPDATE|DELETE)\b)[^\"']*%[sdv]",
        "fmt.Sprintf로 SQL을 조립해 인젝션 위험이 있습니다",
        "매개변수 바인딩(db.Query(\"... ?\", arg))을 사용하세요.",
        ("go",), False,
    ),
    Rule(
        "GO-EXEC-001", "HIGH",
        r"exec\.Command\s*\([^)]*(?:\+|fmt\.Sprintf)",
        "exec.Command 인자에 외부 입력이 결합되어 명령 주입 위험이 있습니다",
        "고정 인자 슬라이스를 쓰고 셸 해석(sh -c)을 피하세요.",
        ("go",), False,
    ),
    Rule(
        "GO-RAND-001", "CRITICAL",
        r"\b(?:math/rand|rand\.(?:Intn|Int63n|Int63|Float64))\b",
        "math/rand로 토큰/키를 생성하면 예측 가능합니다",
        "보안 용도는 crypto/rand를 사용하세요.",
        ("go",), False,
    ),
    Rule(
        "GO-TLS-001", "HIGH",
        r"InsecureSkipVerify\s*:\s*true",
        "TLS 인증서 검증이 비활성화되었습니다",
        "InsecureSkipVerify를 제거하고 신뢰 저장소를 설정하세요.",
        ("go",), False,
    ),
    Rule(
        "GO-HTTP-001", "MEDIUM",
        r"http\.ListenAndServe\s*\(",
        "TLS 없이 평문 HTTP 리스너를 사용할 수 있습니다",
        "http.ListenAndServeTLS 또는 TLS 종단 프록시를 사용하세요.",
        ("go",), False,
    ),
]
