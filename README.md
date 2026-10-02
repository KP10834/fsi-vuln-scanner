# FSI Vuln Scanner

## 프로젝트 개요

Flutter GUI + 번들된 Python 엔진으로 구성된 Windows 데스크톱 앱.
Java/Spring · Go 백엔드 소스를 정적 점검해 금융보안원 2026 분야에 매핑한 취약점 리포트를 생성한다.

## 구성

- `engine/` : Python 점검 엔진 (표준 라이브러리만, 설치 불필요)
- `app/`    : Flutter 데스크톱 UI
- `packaging/` : PyInstaller + flutter build 스크립트

## 엔진 단독 실행 (설치 없이 바로 됨)

```
python -m engine.engine_cli --targets "<path1>,<path2>" --output-dir out --format text
```

결과물:
- `out/security-report.html` — 자체완결형(외부 리소스 없음), 브라우저로 열기
- `out/security-report.json` — 기계판독용 JSON

## 테스트

```
python -m unittest discover -s engine/tests
```

## 데스크톱 앱 빌드 (툴체인 설치 필요)

사전 요구:

1. **Flutter SDK (stable)** 설치 후 `flutter config --enable-windows-desktop`
2. **Visual Studio 2022** 또는 **Build Tools 2019**(16.11+) — "C++를 사용한 데스크톱 개발" 워크로드. `flutter doctor`에서 Visual Studio 항목이 `[√]` 면 충분하다.
3. **Python 3.13+** 설치 후 `pip install pyinstaller` (엔진 자체는 표준 라이브러리만 쓰므로 별도 의존성 없음)
4. **Windows 개발자 모드 켜기** — 설정 → 개발자용 → "개발자 모드" ON. Flutter 플러그인 빌드에 심볼릭 링크가 필요하다.
5. `app/`에 Windows 런너가 없으면 최초 1회: `cd app; flutter create --platforms=windows --project-name fsi_scanner_app .`

빌드:

6. 엔진 빌드: `powershell -File packaging/build_engine.ps1` → `dist/engine/engine.exe`
7. 앱 빌드: `powershell -File packaging/build_app.ps1`

산출물: `app/build/windows/x64/runner/Release/fsi_scanner_app.exe` (옆에 `engine/` 번들 포함)

> `build_engine.ps1`은 `py -3.13`이 없으면 PATH의 `python`으로 자동 폴백한다.

## 설치형 인스톨러 (배포용)

위 Release 번들을 하나의 설치 파일로 패키징한다. Inno Setup 6 필요:

```
winget install -e --id JRSoftware.InnoSetup --source winget
powershell -File packaging/build_installer.ps1
```

산출물: `packaging/dist/FSI-Scanner-Setup.exe`

설치하면 `Program Files\FSI Scanner`에 복사되고, 시작 메뉴·(선택) 바탕화면 바로가기와 제어판 제거 항목이 등록된다.

## 사용 (GUI)

1. `fsi_scanner_app.exe` 실행
2. 검사할 폴더를 창으로 **드래그 앤 드롭**하거나 `[대상 폴더 추가]` 버튼으로 선택 (여러 개 가능)
3. `[스캔 실행]` → 결과 테이블 → HTML 리포트 열기

## 앱 테스트

```
cd app; flutter test
```

## 점검 범위 고지

소스·설정에서 자동 탐지 가능한 금보원 항목의 부분집합만 매핑한다.
공식 항목코드는 비공개이며, 공개된 15개 분야 분류 기준 근사 매핑이다.
인프라(OS/네트워크 장비 등) 전용 항목과 taint 분석은 범위 밖이다.

## 규칙 요약

| 분류 | 규칙 |
|------|------|
| 공용 (공통) | 개인키 하드코딩(SEC-001), API 키 하드코딩(SEC-002), 비밀값 하드코딩(SEC-003), 민감정보 로깅(SEC-004), 와일드카드 CORS(SEC-007) |
| Java/Spring | Actuator 전체 노출(SEC-005), 스택트레이스 노출(SEC-006), @CrossOrigin 와일드카드(JAVA-CORS-001), SQL 문자열 연결(JAVA-SQL-001), 약한 해시(MD5/SHA-1)(JAVA-HASH-001), ECB 블록 모드(JAVA-CIPHER-001), TLS 검증 무력화(JAVA-TLS-001) |
| Go | fmt.Sprintf SQL 조립(GO-SQL-001), exec.Command 주입(GO-EXEC-001), math/rand 사용(GO-RAND-001), InsecureSkipVerify(GO-TLS-001), 평문 HTTP 리스너(GO-HTTP-001) |
