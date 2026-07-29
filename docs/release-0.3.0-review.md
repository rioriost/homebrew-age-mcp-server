# 0.3.0 リリースレビュー

実施日: 2026-07-29

## 判定

0.3.0 のコード、セキュリティ対策、受け入れ済み機能強化は実装済みです。
単体テストのカバレッジは 80% の基準を超えています。Homebrew Formula の公開
URL・SHA256 更新は、最終リリース成果物を公開した後に再確認する必要があります。

## 修正済みの重要事項

| 深刻度 | 問題 | 0.3.0 の対策 |
| --- | --- | --- |
| Critical | グラフ名、Cypher、RETURN 別名を SQL に直接連結していた | `psycopg.sql.Literal` と `Identifier` による安全な SQL 構築へ変更 |
| High | `CREATE(n)` など空白を含まない書き込み句で read-only 判定を回避できた | Cypher AST のトップレベル句で判定し、DB の read-only transaction でも強制 |
| High | `create_graph` / `drop_graph` のグラフ名が SQL injection 可能だった | PostgreSQL パラメータへ変更 |
| High | 接続文字列とパスワードが INFO / DEBUG ログに出力され得た | 接続文字列のログを廃止し、クエリは内容ではなく fingerprint のみ記録 |
| High | `$user` と `public` を含む search path 上の関数を無修飾で実行していた | AGE の関数、型、テーブルを完全修飾し、pool接続のsearch pathを `ag_catalog, pg_catalog` に固定 |
| Medium | 読み取りツールから副作用を持つ `CALL` を実行できた | `CALL` を書き込み扱いに変更 |
| Medium | 行数、クエリ長、実行時間が無制限だった | 50 行、100,000 文字、既定 30 秒の上限を追加 |
| Medium | DB の詳細エラーを MCP クライアントへ返していた | クライアント向けエラーをサニタイズ |
| Medium | 接続文字列を空白で分割・再構築し、引用符付き値を壊していた | libpq / psycopg の conninfo parser を使用 |
| Medium | 書き込み無効時にも破壊的ツールを公開していた | `--allow-write` 時のみ write/create/drop を公開 |
| Low | スキーマ取得が一部のプロパティ・ラベルを欠落させていた | 全プロパティを統合し、エッジのラベル集合を保持 |
| Low | サーバーバージョンが 0.2.8 に固定されていた | インストール済み package metadata から取得 |

## 実装済みの機能強化

1. 公式 Apache AGE コンテナを使う実DB統合テストと専用CI job。
2. `psycopg.AsyncConnectionPool` による同時呼び出し対応。
3. AGE prepared statementによる安全なCypher JSONパラメータ。
4. クエリ入力へ結び付けたHMAC署名付きcursorと、最大50件単位のページネーション。
5. ノード・エッジ件数、方向、サンプルから推定したプロパティ型を含むスキーマ。
6. 全ツールのMCP structured content、JSON互換text content、output schema。
7. クエリ本文・接続情報・値を記録しないOpenTelemetry traces/metrics。

## 品質ゲート

- pytest: 67 unit tests + 1 Apache AGE integration test（Apple containerで通過）
- coverage: 90.23%（最低基準 80%、統合テストを含む）
- Ruff lint / format
- Bandit static security scan
- `uv audit --locked` による OSV 依存脆弱性監査
- sdist / wheel build
- GitHub Actions による継続実行
- Dependabot による uv と GitHub Actions の週次更新

初回 OSV 監査で `mcp`、`cryptography`、`starlette`、`python-multipart`、
`pydantic-settings` に合計 16 件の advisory を検出したため、解消済みバージョンへ
ロックを更新しました。更新後の監査結果は既知脆弱性 0 件です。

## リリース直前の手動作業

1. CI の Apache AGE 統合jobが通過したことを確認し、最小権限ロールでもsmoke testする。
2. `make check` をクリーン環境で実行する。
3. 0.3.0 の sdist / wheel を署名・公開する。
4. 公開した tarball と Formula の SHA256 が一致することを再確認する。
5. Formula の install test を macOS で実行する。
