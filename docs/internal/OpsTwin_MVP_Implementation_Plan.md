# OpsTwin MVP 구현 작업계획 Gantree

**Phase 1**: MVP 구현 (설계 검증 완료 후 실제 구현)
**Date**: 2026-01-04
**Based on**: OpsTwin_Gantree.md, OpsTwin_PPR_Definition_Plan.md
**Status**: Design Phase

---

## 📋 설계 원칙

- **PPR 함수 기반 구현**: Phase 0에서 정의한 63개 PPR 함수를 실제 코드로 구현
- **Top-Down BFS**: 상위 모듈부터 하위 모듈로 점진적 구현
- **Atomic Node 구현**: 15분 내 완료 가능한 최소 단위로 작업
- **테스트 주도**: 각 모듈 구현 후 즉시 단위 테스트 작성

---

## 🗂️ MVP 폴더/파일 구조 Gantree

```text
OpsTwin_MVP_Structure // OpsTwin MVP 전체 폴더 구조 (Design)
    Root // 프로젝트 루트 (Design)
        pyproject.toml // 프로젝트 설정 (Design)
        README.md // 프로젝트 문서 (Design)
        .env.example // 환경변수 템플릿 (Design)
    
    SrcFolder // src/ 소스 코드 (Design)
        OpsTwinPackage // src/opstwin/ 메인 패키지 (Design)
            InitPy // __init__.py 패키지 초기화 (Design)
            ConfigModule // config.py 설정 관리 (Design)
            
            AIWProtocolPackage // src/opstwin/aiw/ AIW 프로토콜 (Design)
                AIW_InitPy // __init__.py (Design)
                ManifestModule // manifest.py (Design)
                DiffStreamModule // diff_stream.py (Design)
                SchemaRegistryModule // schema_registry.py (Design)
                SSEPublisherModule // sse_publisher.py (Design)
            
            TelemetryPackage // src/opstwin/telemetry/ 텔레메트리 (Design)
                Telemetry_InitPy // __init__.py (Design)
                DataCollectorModule // data_collector.py (Design)
                SensorAdapterModule // sensor_adapter.py (Design)
                EventNormalizerModule // event_normalizer.py (Design)
                AnomalyDetectorModule // anomaly_detector.py (Design)
                TimeSeriesDBModule // timeseries_db.py (Design)
            
            PolicyPackage // src/opstwin/policy/ 정책 엔진 (Design)
                Policy_InitPy // __init__.py (Design)
                PermissionModelModule // permission_model.py (Design)
                PolicyEvaluatorModule // policy_evaluator.py (Design)
                ConfidenceScorerModule // confidence_scorer.py (Design)
                ApprovalWorkflowModule // approval_workflow.py (Design)
                RollbackManagerModule // rollback_manager.py (Design)
            
            SimulationPackage // src/opstwin/simulation/ 시뮬레이션 (Design)
                Simulation_InitPy // __init__.py (Design)
                MonteCarloModule // monte_carlo.py (Design)
                QiskitBridgeModule // qiskit_bridge.py (Design)
                HybridCouplerModule // hybrid_coupler.py (Design)
    
    APIFolder // src/api/ FastAPI 서버 (Design)
        API_InitPy // __init__.py (Design)
        MainApp // main.py FastAPI 앱 (Design)
        RoutesFolder // routes/ 라우트 (Design)
            ManifestRoute // manifest.py /.well-known/ (Design)
            DiffRoute // diff.py /diff, /subscribe (Design)
            TelemetryRoute // telemetry.py /telemetry/ingest (Design)
            SimRoute // sim.py /sim/run (Design)
            ActionRoute // action.py /actions, /proposals (Design)
    
    SchemasFolder // schemas/ JSON 스키마 (Design)
        TelemetrySchemaJSON // telemetry.v1.json (Design)
        AnomalySchemaJSON // anomaly.v1.json (Design)
        PolicySchemaJSON // policy.v1.json (Design)
        ActionSchemaJSON // action.v1.json (Design)
        SimSchemaJSON // sim.v1.json (Design)
    
    TestsFolder // tests/ 테스트 (Design)
        Tests_InitPy // __init__.py (Design)
        ConfTestPy // conftest.py pytest 설정 (Design)
        UnitTestsFolder // unit/ 단위 테스트 (Design)
            Test_AIW // test_aiw.py (Design)
            Test_Telemetry // test_telemetry.py (Design)
            Test_Policy // test_policy.py (Design)
            Test_Simulation // test_simulation.py (Design)
        IntegrationTestsFolder // integration/ 통합 테스트 (Design)
            Test_E2E_Flow // test_e2e_flow.py (Design)
            Test_API // test_api.py (Design)
    
    DockerFolder // docker/ Docker 설정 (Design)
        Dockerfile // Dockerfile (Design)
        DockerCompose // docker-compose.yml (Design)
```

---

## 🌲 Main Gantree: MVP 구현 작업계획

```text
OpsTwin_MVP_Implementation // OpsTwin MVP 구현 프로젝트 (Design)
    Phase1_1_Core_AIW // Phase 1.1: Core AIW 구현 (Design)
        ProjectSetup // 프로젝트 초기 설정 (Design)
            CreatePyproject // pyproject.toml 생성 (Design)
            CreatePackageStructure // 패키지 구조 생성 (Design)
            SetupDependencies // 의존성 설치 (Design)
        ManifestImplementation // Manifest 구현 (Design)
            ManifestEndpoint // /.well-known/aiw-manifest.json 엔드포인트 (Design)
            ManifestSchemaValidation // 스키마 검증 (Design)
        DiffStreamImplementation // DiffStream 구현 (Design)
            DiffEndpoint // /diff?since={cursor} 엔드포인트 (Design)
            CursorManagement // 커서 관리 로직 (Design)
        SSEImplementation // SSE 구현 (Design)
            SubscribeEndpoint // /subscribe SSE 엔드포인트 (Design)
            EventPublishing // 이벤트 발행 로직 (Design)
        SchemaRegistryImplementation // SchemaRegistry 구현 (Design)
            SchemasEndpoint // /schemas 엔드포인트 (Design)
            SchemaValidation // 스키마 검증 유틸리티 (Design)
    
    Phase1_2_Core_Telemetry // Phase 1.2: Core Telemetry 구현 (Design)
        SensorAdapterImplementation // SensorAdapter 구현 (Design)
            MQTTAdapter // MQTT 어댑터 (MVP 1종) (Design)
            AdapterInterface // 어댑터 인터페이스 (Design)
        EventNormalizerImplementation // EventNormalizer 구현 (Design)
            JSONNormalizer // JSON 정규화 (Design)
            TimestampParser // 타임스탬프 파싱 (Design)
        TimeSeriesDBAdapter // TimescaleDB 어댑터 (Design)
            ConnectionPool // 연결 풀 관리 (Design)
            BatchInsert // 배치 삽입 (Design)
        TelemetryIngestEndpoint // /telemetry/ingest 엔드포인트 (Design)
            IngestValidation // 입력 검증 (Design)
            StoreAndPublish // 저장 및 이벤트 발행 (Design)
    
    Phase1_3_Core_Policy // Phase 1.3: Core Policy 구현 (Design)
        PermissionCheckerImplementation // PermissionChecker 구현 (Design)
            RBACValidator // RBAC 검증 로직 (Design)
            TokenParser // 토큰 파싱 (Design)
        ConfidenceScorerImplementation // ConfidenceScorer 구현 (Design)
            DataQualityScore // 데이터 품질 점수 (Design)
            SimConsistencyScore // 시뮬레이션 일관성 점수 (Design)
            WeightedAggregation // 가중 평균 집계 (Design)
        DecisionMakerImplementation // DecisionMaker 구현 (Design)
            ThresholdEvaluator // 임계값 평가 (Design)
            DecisionRouter // 결정 라우터 (auto/approve/analyze) (Design)
        ProposalEndpoint // /proposals 엔드포인트 (Design)
            ProposalCreate // 제안 생성 (Design)
            ProposalApprove // 제안 승인 (Design)
    
    Phase1_4_Core_Simulation // Phase 1.4: Core Simulation 구현 (Design)
        MonteCarloImplementation // MonteCarloEngine 구현 (Design)
            RandomSampler // 무작위 샘플러 (Design)
            StatisticsCollector // 통계 수집 (Design)
            ConvergenceChecker // 수렴 검사 (Design)
        QiskitBridgeImplementation // QiskitBridge 구현 (Decomposed)
        SimRunEndpoint // /sim/run 엔드포인트 (Design)
            SimRequest // 시뮬레이션 요청 처리 (Design)
            ResultCaching // 결과 캐싱 (Design)
    
    Phase1_5_Integration_Test // Phase 1.5: 통합 테스트 (Design)
        UnitTestSuite // 단위 테스트 스위트 (Design)
            AIW_UnitTests // AIW 단위 테스트 (Design)
            Telemetry_UnitTests // Telemetry 단위 테스트 (Design)
            Policy_UnitTests // Policy 단위 테스트 (Design)
            Simulation_UnitTests // Simulation 단위 테스트 (Design)
        IntegrationTestSuite // 통합 테스트 스위트 (Design)
            E2E_HappyPath // E2E 정상 흐름 테스트 (Design)
            E2E_ErrorHandling // E2E 에러 처리 테스트 (Design)
        APITestSuite // API 테스트 스위트 (Design)
            ManifestAPITest // Manifest API 테스트 (Design)
            DiffAPITest // Diff API 테스트 (Design)
            TelemetryAPITest // Telemetry API 테스트 (Design)
```

---

## 🌲 Decomposed Tree: QiskitBridgeImplementation

```text
QiskitBridgeImplementation // QiskitBridge 구현 (Design)
    CircuitBuilderImpl // CircuitBuilder 구현 (Design)
        GateSequencer // 게이트 시퀀서 (Design)
        ParameterBinder // 파라미터 바인더 (Design)
    NoiseModelLoaderImpl // NoiseModelLoader 구현 (Design)
        BackendProfiler // 백엔드 프로파일러 (Design)
        ErrorRateConfig // 에러율 설정 (Design)
    ResultParserImpl // ResultParser 구현 (Design)
        CountsExtractor // 카운트 추출 (Design)
        ExpectationValue // 기대값 계산 (Design)
```

---

## 📊 구현 통계 및 일정

| Phase | 모듈 수 | 예상 시간 | 우선순위 |
| :--- | :--- | :--- | :--- |
| 1.1 Core AIW | 5개 | 8시간 | P0 |
| 1.2 Core Telemetry | 4개 | 6시간 | P0 |
| 1.3 Core Policy | 4개 | 8시간 | P1 |
| 1.4 Core Simulation | 3개 | 6시간 | P1 |
| 1.5 Integration Test | 3개 | 4시간 | P0 |
| **Total** | **19개** | **32시간** | - |

---

## 🎯 MVP 성공 기준

```text
MVP_Success_Criteria // MVP 성공 기준 (Design)
    Functional_Criteria // 기능 요구사항 (Design)
        SC01_ManifestDiscovery // /.well-known/aiw-manifest.json 응답 (Design)
        SC02_TelemetryIngest // /telemetry/ingest 성공 + 이벤트 발행 (Design)
        SC03_DiffSync // /diff?since= 커서 동기화 (Design)
        SC04_SSEStream // /subscribe SSE 이벤트 수신 (Design)
        SC05_SimRun // /sim/run 시뮬레이션 실행 (Design)
    NonFunctional_Criteria // 비기능 요구사항 (Design)
        SC06_Latency // SSE 이벤트 지연 < 1초 (p95) (Design)
        SC07_TestCoverage // 단위 테스트 커버리지 >= 80% (Design)
        SC08_DockerBuild // Docker 이미지 빌드 성공 (Design)
```

---

## 📂 파일 생성 순서 (실행 계획)

```text
Execution_Order // 파일 생성 순서 (Design)
    Step1_ProjectSetup // 1단계: 프로젝트 설정 (Design)
        Create_pyproject_toml // pyproject.toml 생성 (Design)
        Create_src_opstwin_init // src/opstwin/__init__.py (Design)
        Create_src_api_main // src/api/main.py FastAPI 앱 (Design)
    
    Step2_Core_AIW // 2단계: AIW 코어 (Design)
        Create_aiw_manifest // src/opstwin/aiw/manifest.py (Design)
        Create_aiw_diff_stream // src/opstwin/aiw/diff_stream.py (Design)
        Create_aiw_sse_publisher // src/opstwin/aiw/sse_publisher.py (Design)
        Create_schemas_json // schemas/*.json (5개) (Design)
        Create_routes_manifest // src/api/routes/manifest.py (Design)
        Create_routes_diff // src/api/routes/diff.py (Design)
    
    Step3_Core_Telemetry // 3단계: Telemetry 코어 (Design)
        Create_telemetry_sensor_adapter // src/opstwin/telemetry/sensor_adapter.py (Design)
        Create_telemetry_event_normalizer // src/opstwin/telemetry/event_normalizer.py (Design)
        Create_telemetry_timeseries_db // src/opstwin/telemetry/timeseries_db.py (Design)
        Create_routes_telemetry // src/api/routes/telemetry.py (Design)
    
    Step4_Core_Policy // 4단계: Policy 코어 (Design)
        Create_policy_permission // src/opstwin/policy/permission_model.py (Design)
        Create_policy_evaluator // src/opstwin/policy/policy_evaluator.py (Design)
        Create_policy_confidence // src/opstwin/policy/confidence_scorer.py (Design)
        Create_routes_action // src/api/routes/action.py (Design)
    
    Step5_Core_Simulation // 5단계: Simulation 코어 (Design)
        Create_sim_monte_carlo // src/opstwin/simulation/monte_carlo.py (Design)
        Create_sim_qiskit_bridge // src/opstwin/simulation/qiskit_bridge.py (Design)
        Create_routes_sim // src/api/routes/sim.py (Design)
    
    Step6_Tests // 6단계: 테스트 (Design)
        Create_conftest // tests/conftest.py (Design)
        Create_unit_tests // tests/unit/*.py (4개) (Design)
        Create_integration_tests // tests/integration/*.py (2개) (Design)
    
    Step7_Docker // 7단계: Docker (Design)
        Create_dockerfile // docker/Dockerfile (Design)
        Create_docker_compose // docker/docker-compose.yml (Design)
```

---

## 🔧 기술 스택

| 영역 | 기술 | 버전 |
| :--- | :--- | :--- |
| API Framework | FastAPI | 0.109+ |
| ASGI Server | Uvicorn | 0.27+ |
| Database | TimescaleDB | 2.x |
| Message Queue | Kafka | 3.x |
| Quantum SDK | Qiskit | 1.0+ |
| Testing | pytest | 8.x |
| Containerization | Docker | 24.x |

---

## 📝 PPR 함수 → 실제 코드 매핑

| PPR 함수 | 실제 파일 | 클래스/함수 |
| :--- | :--- | :--- |
| `AI_make_manifest()` | `aiw/manifest.py` | `ManifestBuilder.build()` |
| `AI_make_diff_engine()` | `aiw/diff_stream.py` | `DiffEngine.get_events()` |
| `AI_make_sensor_adapter()` | `telemetry/sensor_adapter.py` | `MQTTSensorAdapter` |
| `AI_make_confidence_scorer()` | `policy/confidence_scorer.py` | `ConfidenceScorer.calculate()` |
| `AI_make_monte_carlo_engine()` | `simulation/monte_carlo.py` | `MonteCarloEngine.run()` |

---

## ✅ 검증 계획

### 자동화 테스트

```bash
# 단위 테스트
pytest tests/unit/ -v --cov=src/opstwin --cov-report=term-missing

# 통합 테스트
pytest tests/integration/ -v

# API 테스트
pytest tests/integration/test_api.py -v
```

### 수동 검증

1. **Manifest 검증**: `curl http://localhost:8000/.well-known/aiw-manifest.json`
2. **Telemetry Ingest**: POST 요청으로 텔레메트리 데이터 전송
3. **SSE 스트림**: EventSource로 `/subscribe` 연결 확인
4. **Docker 빌드**: `docker-compose up --build` 성공 확인

---

## 📌 다음 단계

이 문서 승인 후:

1. Phase 1.1 Core AIW 노드들을 `InProgress`로 전환
2. `pyproject.toml` 및 프로젝트 구조 생성부터 시작
3. 각 단계 완료 시 테스트 작성 및 실행
