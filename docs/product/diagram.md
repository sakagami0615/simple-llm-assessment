# システムダイアグラム

## 概要

`local-llm-eval` は、設定解決と外部評価フレームワークの起動を分離した CLI アプリケーションである。モデル推論や採点は lm-evaluation-harness / OpenCompass に委譲し、本体は薄い orchestration 層に留める。

## システムコンテキスト図

```mermaid
flowchart LR
    User[利用者]
    CLI[local-llm-eval CLI]
    Config[config/*.yaml]
    Dataset[datasets/*.json]
    LocalLLM[ローカル LLM サーバ<br/>OpenAI 互換 API]
    LMEval[lm-evaluation-harness]
    OpenCompass[OpenCompass]
    Runs[runs/]

    User --> CLI
    CLI --> Config
    CLI --> Dataset
    CLI --> LMEval
    CLI --> OpenCompass
    LMEval --> LocalLLM
    OpenCompass --> LocalLLM
    CLI --> Runs
```

## コンポーネント図

```mermaid
flowchart TB
    subgraph Package[src/local_llm_eval]
        CLI[cli.py<br/>validate / run]
        Config[config.py<br/>YAML 読み込みと検証]
        Planner[planner.py<br/>suite 参照解決と job 展開]
        Executor[executor.py<br/>実行と summary 保存]
        Results[results.py<br/>UTF-8 JSON 書き出し]
        RunnerLM[runners/lm_evaluation_harness.py<br/>lm-eval コマンド生成]
        RunnerOC[runners/opencompass.py<br/>OpenCompass config / コマンド生成]
    end

    CLI --> Planner
    Planner --> Config
    CLI --> Executor
    Executor --> RunnerLM
    Executor --> RunnerOC
    Executor --> Results
```

## クラス図

```mermaid
classDiagram
    class ModelConfig {
        +str id
        +str provider
        +str base_url
        +str model
        +str? api_key_env
        +dict generation
        +Path path
    }

    class BenchmarkConfig {
        +str id
        +str runner
        +str? task
        +str? dataset
        +str? dataset_format
        +str? evaluator
        +dict runner_params
        +list metrics
        +Path path
    }

    class SuiteConfig {
        +str id
        +list models
        +list benchmarks
        +Path path
    }

    class EvaluationPlan {
        +SuiteConfig suite
        +list models
        +list benchmarks
        +list jobs
    }

    class EvaluationJob {
        +ModelConfig model
        +BenchmarkConfig benchmark
        +str output_name
    }

    class ExecutionResult {
        +Path run_dir
    }

    SuiteConfig "1" --> "*" ModelConfig : references
    SuiteConfig "1" --> "*" BenchmarkConfig : references
    EvaluationPlan "1" --> "1" SuiteConfig
    EvaluationPlan "1" --> "*" EvaluationJob
    EvaluationJob "1" --> "1" ModelConfig
    EvaluationJob "1" --> "1" BenchmarkConfig
    ExecutionResult "1" --> "1" EvaluationPlan : generated from
```

## シーケンス図

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Planner
    participant Config
    participant Executor
    participant Runner
    participant Framework
    participant Runs

    User->>CLI: local-llm-eval run suite.yaml
    CLI->>Planner: plan_suite(suite)
    Planner->>Config: load suite/model/benchmark YAML
    Config-->>Planner: validated dataclasses
    Planner-->>CLI: EvaluationPlan
    CLI->>Executor: execute_plan(plan)
    Executor->>Runs: write run.yaml.json
    loop each job
        Executor->>Runner: build command
        Runner-->>Executor: command
        alt dry-run
            Executor->>Runs: record skipped
        else run
            Executor->>Framework: execute command
            Framework-->>Executor: exit code
            Executor->>Runs: record success or failed
        end
    end
    Executor->>Runs: write summary.json
```

## データフロー図

```mermaid
flowchart LR
    Suite[suite YAML]
    Models[model YAML]
    Benchmarks[benchmark YAML]
    Plan[EvaluationPlan]
    Jobs[EvaluationJob]
    Command[runner command]
    Summary[summary.json]

    Suite --> Models
    Suite --> Benchmarks
    Models --> Plan
    Benchmarks --> Plan
    Plan --> Jobs
    Jobs --> Command
    Command --> Summary
```

## データモデル / 永続化図

```mermaid
flowchart TB
    ConfigRoot[config/]
    Models[models/*.yaml]
    Benchmarks[benchmarks/*.yaml]
    Suites[suites/*.yaml]
    Datasets[datasets/*.json]
    Runs[runs/<timestamp>-<suite>/]
    RunJson[run.yaml.json]
    Summary[summary.json]
    Raw[raw/<model.id>/<benchmark.id>/]

    ConfigRoot --> Models
    ConfigRoot --> Benchmarks
    ConfigRoot --> Suites
    Suites --> Models
    Suites --> Benchmarks
    Benchmarks --> Datasets
    Runs --> RunJson
    Runs --> Summary
    Runs --> Raw
```

## エラー時フロー

```mermaid
flowchart TB
    Start[CLI 実行]
    Plan[設定読み込み / 参照解決]
    ConfigError{ConfigError?}
    Stderr[標準エラーへ configuration error を出力]
    Exit2[終了コード 2]
    Execute[ジョブ実行]
    ExitCode{外部コマンド終了コード}
    Success[summary に success を記録]
    Failed[summary に failed と exit_code を記録]
    Continue[後続ジョブを継続]

    Start --> Plan
    Plan --> ConfigError
    ConfigError -- yes --> Stderr --> Exit2
    ConfigError -- no --> Execute
    Execute --> ExitCode
    ExitCode -- 0 --> Success
    ExitCode -- non-zero --> Failed --> Continue
    Success --> Continue
```
