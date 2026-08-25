#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "data" / "corpus.jsonl"
QUERIES_PATH = ROOT / "data" / "evaluation_queries.json"


def document(
    *, id: str, family: str, title: str, filename: str, category: str,
    body: str, identifiers: list[str] | None = None,
    parent_id: str | None = None, chunk_order: int | None = None,
    document_type: str, product_category: str | None = None,
    device_age_months: int | None = None,
    support_outcome: str | None = None,
) -> dict[str, Any]:
    return {
        "id": id, "family": family, "title": title, "filename": filename,
        "category": category, "page_start": 1, "identifiers": identifiers or [],
        "parent_id": parent_id, "chunk_order": chunk_order,
        "document_type": document_type, "product_category": product_category,
        "device_age_months": device_age_months,
        "support_outcome": support_outcome, "synthetic": True, "body": body,
    }


def build_products() -> list[dict[str, Any]]:
    rows = [
        ("WM-A410", "washer", "ドラム式洗濯乾燥機です。自動投入、温水洗浄、スマートフォンからの運転予約に対応します。無線LANは2.4GHz帯を使用します。"),
        ("WM-A410S", "washer", "WM-A410の小型モデルです。乾燥容量とドラム径が異なり、交換部品や一部のエラー内容はWM-A410と共通ではありません。"),
        ("WM-A401", "washer", "洗濯容量10kgの旧世代モデルです。スマートフォン連携には対応せず、本体パネルから運転コースを選択します。"),
        ("DR-B220", "dryer", "ヒートポンプ式衣類乾燥機です。湿度センサーで乾燥時間を調整し、フィルター詰まりを検知すると運転を停止します。"),
        ("DR-B202", "dryer", "電気ヒーター式の衣類乾燥機です。排気ダクトが必要で、DR-B220用のフィルターは装着できません。"),
        ("AC-C300", "air_conditioner", "無線LAN内蔵のルームエアコンです。外出先操作、室温通知、フィルター清掃時期の通知に対応します。"),
        ("AC-C330", "air_conditioner", "寒冷地向けルームエアコンです。低温暖房能力を強化していますが、AC-C300とは室外機と更新ファイルが異なります。"),
        ("RF-D510", "refrigerator", "容量510Lの冷蔵庫です。自動製氷、急速冷凍、扉の閉め忘れ通知をスマートフォンで確認できます。"),
        ("RF-D501", "refrigerator", "容量500Lの冷蔵庫です。自動製氷に対応しますが、ネットワーク機能と遠隔通知には対応しません。"),
        ("OV-E600", "oven", "過熱水蒸気オーブンレンジです。温度センサーと重量センサーを使い、自動調理とスチーム洗浄を行います。"),
        ("OV-E660", "oven", "業務向けの大容量オーブンです。OV-E600と名称は似ていますが、電源、設置間隔、エラーコード体系が異なります。"),
        ("VC-F710", "vacuum", "コードレス掃除機です。着脱式バッテリー、床面検知、自動吸引力調整に対応します。"),
        ("VC-F701", "vacuum", "軽量コードレス掃除機です。VC-F710用バッテリーとは電圧が異なり、相互に取り付けられません。"),
        ("TV-G800", "television", "4K液晶テレビです。動画配信アプリ、無線LAN、Bluetooth音声出力、録画機能に対応します。"),
        ("TV-G880", "television", "有機ELテレビです。TV-G800と同じ操作アプリを使えますが、パネル保護と壁掛け金具の条件が異なります。"),
    ]
    return [document(
        id=f"product-{model.lower()}", family="products", title="製品カタログ 2026年版",
        filename="product-catalog-2026.pdf", category="製品", body=body,
        identifiers=[model, f"PRODUCT-{model}"], document_type="product",
        product_category=category,
    ) for model, category, body in rows]


def build_error_codes() -> list[dict[str, Any]]:
    rows = [
        ("WM-A410", "E42", "washer", "給水を開始できないエラーです。蛇口、給水ホース、給水口フィルターを確認します。排水異常を示すE24とは対処が異なります。"),
        ("WM-A410", "E24", "washer", "排水を完了できないエラーです。排水ホースの折れと糸くずフィルターを確認します。給水側の点検では解消しません。"),
        ("WM-A410S", "E42", "washer", "ドアロックを確認できないエラーです。WM-A410のE42とは意味が異なるため、給水ホースではなく扉の異物を点検します。"),
        ("WM-A401", "E42", "washer", "水位センサーの応答が規定範囲外であることを示します。電源を切っても再発する場合は点検を依頼します。"),
        ("DR-B220", "E42", "dryer", "乾燥室の温度上昇を検知したエラーです。吸気口とフィルターを清掃し、冷却後に再開します。"),
        ("AC-C300", "E24", "air_conditioner", "室内機と室外機の通信が途切れたことを示します。ブレーカーと接続線を確認し、無線LAN設定は変更しません。"),
        ("AC-C300", "E42", "air_conditioner", "排水経路の詰まりを検知したエラーです。ドレンホースの折れや逆勾配を確認します。"),
        ("RF-D510", "E17", "refrigerator", "製氷皿が所定位置へ戻れないエラーです。氷の固着を除き、製氷室を空にして再試行します。"),
        ("OV-E600", "E17", "oven", "庫内温度センサーの値を取得できないエラーです。加熱を中止し、電源を入れ直しても続く場合は修理を依頼します。"),
        ("VC-F710", "E31", "vacuum", "回転ブラシの拘束を検知したエラーです。髪の毛や糸を取り除き、ブラシが手で回ることを確認します。"),
        ("TV-G800", "E31", "television", "配信サービスとの認証に失敗したエラーです。ネットワーク接続と本体時刻を確認します。"),
        ("WM-A410", "C07", "washer", "洗剤自動投入タンクが正しく装着されていない通知です。運転はできますが、自動投入は行われません。"),
        ("WM-A410", "U11", "washer", "排水に通常より時間がかかっている通知です。E24になる前に排水フィルターを清掃します。"),
        ("DR-B220", "U11", "dryer", "乾燥フィルターの清掃時期を示す通知です。故障ではなく、清掃後に通知をリセットします。"),
        ("RF-D510", "C07", "refrigerator", "冷蔵室の扉が一定時間開いている通知です。扉を閉めても続く場合は食品の挟まりを確認します。"),
    ]
    return [document(
        id=f"error-{model.lower()}-{code.lower()}", family="error-codes",
        title=f"{model} エラーコード一覧", filename="error-code-reference-2026.pdf",
        category="エラー", body=body, identifiers=[model, code, f"{model}-{code}"],
        document_type="error_code", product_category=category,
    ) for model, code, category, body in rows]


def build_connectivity_cases() -> list[dict[str, Any]]:
    rows = [
        ("01", "washer", 3, 8, "resolved", "WM-A410をファームウェア3へ更新後、アプリから見つからなくなりました。登録を解除して同じ家庭内ネットワークで再登録すると接続できるようになりました。"),
        ("02", "air_conditioner", 3, 14, "unresolved", "AC-C300は無線LANへ接続済みですが、スマートフォンのローカルネットワーク権限が許可されておらず、アプリから操作できない状態が続きました。"),
        ("03", "washer", 4, 18, "unresolved", "WM-A410をファームウェア4へ更新しましたが、更新完了後もスマートフォンとの接続が回復しませんでした。再登録とルーター再起動でも未解決です。"),
        ("04", "washer", 2, 30, "unresolved", "WM-A410のファームウェアは2のままで、アプリの新しい認証方式に対応できず接続できませんでした。更新作業はまだ行っていません。"),
        ("05", "refrigerator", 4, 10, "resolved", "RF-D510の更新後に通知が届かなくなりました。ルーターと冷蔵庫を再起動するとクラウド接続が復旧し、扉通知も届くようになりました。"),
        ("06", "television", 3, 6, "resolved", "TV-G800はアプリから操作できましたが、番組開始通知だけが遅れていました。通知権限を有効にすると解消しました。"),
        ("07", "air_conditioner", 3, 20, "unresolved", "ルーター交換後、AC-C300を新しいSSIDへ登録しても外出先操作を利用できませんでした。本体操作はできますが、クラウド接続は未解決です。"),
        ("08", "oven", 4, 9, "resolved", "OV-E600がアプリに表示されなくなりました。アプリを再インストールして製品を再登録すると接続が回復しました。"),
        ("09", "vacuum", 3, 16, "unresolved", "VC-F710はBluetoothで検出できますが、クラウドアカウントへの紐付けが完了せず、履歴を同期できませんでした。"),
        ("10", "television", 5, 22, "resolved", "TV-G880の更新直後にリモート操作が失敗しました。設定を保持したまま更新を再適用すると接続できる状態へ戻りました。"),
        ("11", "washer", 3, 13, "unresolved", "WM-A410を5GHz専用SSIDへ接続しようとして失敗しました。2.4GHz帯のSSIDが用意されるまでアプリ連携は利用できませんでした。"),
        ("12", "refrigerator", 4, 11, "unresolved", "RF-D510はルーターへ接続して通知も送信していますが、アプリ画面だけがオフライン表示のままでした。キャッシュ削除でも表示は直りませんでした。"),
        ("13", "air_conditioner", 3, 7, "resolved", "AC-C300をファームウェア3へ更新した後、一度は接続が切れましたが、本体の再起動だけでアプリ操作が再開できました。"),
        ("14", "washer", 4, 25, "unresolved", "スマートフォンを交換した後、WM-A410を新端末へ登録できませんでした。旧端末の登録解除を行っても接続できない状態が続きました。"),
        ("15", "washer", 2, 28, "resolved", "旧ファームウェアのWM-A410で一時的に接続が切れましたが、ルーターのDHCP更新後は再発せず、現在は接続できています。"),
    ]
    return [document(
        id=f"support-connect-{slug}", family="connectivity-cases",
        title=f"接続サポート事例 2025-{slug}", filename="connectivity-support-cases-2025.pdf",
        category="サポート事例", body=body, identifiers=[f"CASE-CONNECT-{slug}"],
        document_type="support_case", product_category=category,
        device_age_months=age, support_outcome=outcome,
    ) for slug, category, _firmware, age, outcome, body in rows]


def build_repair_cases() -> list[dict[str, Any]]:
    rows = [
        ("01", "washer", 3, 20, "resolved", "給水が遅いWM-A410を点検し、給水口フィルターの砂を除去しました。部品交換は行わず、規定時間内に給水できることを確認しました。"),
        ("02", "dryer", 2, 15, "resolved", "DR-B220が途中停止しましたが、フィルター清掃後は正常に乾燥できました。温度部品の交換は不要でした。"),
        ("03", "dryer", 2, 26, "unresolved", "DR-B220のフィルターを清掃しても過熱停止が再発しました。温度センサー交換が必要ですが、訪問時に部品がなく未解決です。"),
        ("04", "refrigerator", 2, 40, "resolved", "RF-D510の製氷皿に氷が固着していました。氷を除去して給水経路を清掃すると製氷を再開しました。"),
        ("05", "oven", 2, 12, "resolved", "OV-E600が予熱を完了しない申告でした。庫内の温度センサー周辺の汚れを清掃し、設定温度へ到達することを確認しました。"),
        ("06", "vacuum", 3, 19, "unresolved", "VC-F710の回転ブラシを清掃してもE31が再発しました。モーター交換の見積りを案内し、修理は保留になりました。"),
        ("07", "television", 5, 9, "resolved", "TV-G800で配信アプリだけ音が出ない状態でした。音声出力設定をPCMへ変更すると解消し、基板交換は不要でした。"),
        ("08", "air_conditioner", 4, 31, "unresolved", "AC-C300の冷房が弱く、フィルター清掃後も改善しませんでした。冷媒漏れが疑われ、後日の再訪問となりました。"),
        ("09", "washer", 4, 17, "resolved", "WM-A410の排水エラーE24は、排水ホースの折れを直すと解消しました。給水弁と水位センサーには異常がありませんでした。"),
        ("10", "refrigerator", 2, 52, "unresolved", "RF-D501の冷蔵室が冷えず、霜取り後も温度が下がりませんでした。圧縮機の点検が必要なため持ち帰り修理となりました。"),
        ("11", "washer", 4, 21, "unresolved", "WM-A410でE42が表示され、蛇口とホースを確認しても給水できませんでした。給水弁の交換部品を手配し、作業は未完了です。"),
        ("12", "oven", 2, 33, "resolved", "OV-E600のスチーム量が少ない状態は、給水タンクの弁に付着した水あかを除去すると改善しました。"),
        ("13", "vacuum", 3, 14, "resolved", "VC-F710の運転時間が短い申告に対し、劣化したバッテリーを交換しました。標準モードの連続運転時間へ戻りました。"),
        ("14", "television", 5, 24, "unresolved", "TV-G880の画面に縦線が出るためパネル交換が必要と判断しました。部品納期を案内し、修理完了待ちです。"),
        ("15", "air_conditioner", 3, 18, "resolved", "AC-C330の室外機が始動しない状態は、ブレーカー復帰と端子の締め直しで解消しました。"),
    ]
    return [document(
        id=f"repair-case-{slug}", family="repair-cases",
        title=f"訪問修理事例 2025-{slug}", filename="repair-cases-2025.pdf",
        category="修理事例", body=body, identifiers=[f"CASE-REPAIR-{slug}"],
        document_type="repair_case", product_category=category,
        device_age_months=age, support_outcome=outcome,
    ) for slug, category, _firmware, age, outcome, body in rows]


def build_simple_family(
    *, family: str, title: str, filename: str, category: str,
    document_type: str, rows: list[tuple[str, str, str, str]],
) -> list[dict[str, Any]]:
    return [document(
        id=f"{family}-{slug}", family=family, title=title, filename=filename,
        category=category, body=body, identifiers=[identifier],
        document_type=document_type, product_category=product_category,
    ) for slug, identifier, product_category, body in rows]


def build_manuals() -> list[dict[str, Any]]:
    rows = [
        ("wm-water", "MANUAL-WM-WATER", "washer", "洗濯機へ水が入らない場合は、蛇口が開いていること、給水ホースが折れていないこと、給水口フィルターに異物がないことを順に確認します。"),
        ("wm-drain", "MANUAL-WM-DRAIN", "washer", "排水できない場合は、糸くずフィルター、排水ホースの高さと折れ、排水口の詰まりを確認します。"),
        ("dryer-filter", "MANUAL-DR-FILTER", "dryer", "乾燥運転ごとに糸くずフィルターを清掃します。目詰まりしたまま運転すると乾燥時間が延び、過熱停止することがあります。"),
        ("ac-pairing", "MANUAL-AC-PAIR", "air_conditioner", "エアコンをアプリへ登録するときは、2.4GHzの無線LANへスマートフォンを接続し、本体の接続ボタンを5秒押します。"),
        ("ac-clean", "MANUAL-AC-CLEAN", "air_conditioner", "フィルターを外して掃除機でほこりを取り、水洗い後は陰干しで完全に乾かしてから戻します。"),
        ("fridge-temp", "MANUAL-RF-TEMP", "refrigerator", "冷蔵室が冷えにくい場合は、食品の詰め込み、吹出口のふさがり、扉パッキンの隙間、周囲温度を確認します。"),
        ("fridge-ice", "MANUAL-RF-ICE", "refrigerator", "自動製氷を再開する前に、給水タンクを洗い、製氷皿に固着した氷がないことを確認します。"),
        ("oven-preheat", "MANUAL-OV-PREHEAT", "oven", "予熱中は扉を開けず、空の角皿だけを指定段へ入れます。庫内が汚れていると温度検知に時間がかかります。"),
        ("oven-steam", "MANUAL-OV-STEAM", "oven", "スチームを使う前に給水タンクへ水を入れ、タンク弁と蒸気口に水あかがないことを確認します。"),
        ("vacuum-brush", "MANUAL-VC-BRUSH", "vacuum", "回転ブラシへ絡んだ髪や糸は電源を切ってから取り除きます。軸受け部へ油を差してはいけません。"),
        ("vacuum-dust", "MANUAL-VC-DUST", "vacuum", "ダストカップのごみを捨て、フィルターを水洗いした場合は24時間以上乾燥させてから装着します。"),
        ("tv-network", "MANUAL-TV-NET", "television", "配信アプリが開かない場合は、テレビの時刻、ネットワーク診断、サービス稼働状況の順に確認します。"),
        ("tv-audio", "MANUAL-TV-AUDIO", "television", "外部機器から音が出ない場合は、入力端子、音声形式、ARC設定、消音状態を確認します。"),
        ("app-account", "MANUAL-APP-ACCOUNT", "app", "製品を別のスマートフォンへ移す場合は、旧端末から登録解除して同じアカウントで新端末へログインします。"),
        ("router-reset", "MANUAL-ROUTER-RESET", "network", "ルーターを再起動するときは電源を抜いて30秒待ち、起動完了後に家電を再接続します。初期化ボタンは押しません。"),
    ]
    return build_simple_family(family="manual", title="製品サポートガイド", filename="support-manual-2026.pdf", category="取扱説明", document_type="manual", rows=rows)


def build_firmware_notes() -> list[dict[str, Any]]:
    rows = [
        ("wm-a410-3", "FW-WM-A410-3", "washer", "WM-A410ファームウェア3では、予約運転の同期と無線LAN再接続処理を改善しました。更新後にアプリの再登録が必要な場合があります。"),
        ("wm-a410-4", "FW-WM-A410-4", "washer", "WM-A410ファームウェア4では、認証方式を更新し、接続履歴の保存を改善しました。更新中は電源を切らないでください。"),
        ("wm-a410s-3", "FW-WM-A410S-3", "washer", "WM-A410S専用ファームウェア3です。WM-A410へ適用すると起動できないため、型番を確認して更新します。"),
        ("ac-c300-3", "FW-AC-C300-3", "air_conditioner", "AC-C300ファームウェア3では、外出先操作の再接続と室温通知の遅延を改善しました。"),
        ("ac-c300-4", "FW-AC-C300-4", "air_conditioner", "AC-C300ファームウェア4では、WPA3移行時の接続処理を追加しました。旧ルーターでは設定変更は不要です。"),
        ("ac-c330-4", "FW-AC-C330-4", "air_conditioner", "AC-C330専用の低温運転制御を更新します。AC-C300用ファイルとの互換性はありません。"),
        ("rf-d510-2", "FW-RF-D510-2", "refrigerator", "RF-D510ファームウェア2では、扉通知と製氷完了通知が重複する問題を修正しました。"),
        ("ov-e600-2", "FW-OV-E600-2", "oven", "OV-E600ファームウェア2では、自動調理終了後にアプリへ結果が反映されない問題を修正しました。"),
        ("vc-f710-3", "FW-VC-F710-3", "vacuum", "VC-F710ファームウェア3では、床面検知の切替えと清掃履歴の同期を改善しました。"),
        ("tv-g800-5", "FW-TV-G800-5", "television", "TV-G800ファームウェア5では、配信アプリの認証更新とBluetooth音声の遅延を改善しました。"),
        ("tv-g880-5", "FW-TV-G880-5", "television", "TV-G880ファームウェア5では、パネル保護処理と配信アプリの起動を改善しました。"),
        ("app-240", "APP-2.4.0", "app", "アプリ2.4.0では製品一覧のオフライン表示を修正し、旧ファームウェア2の製品も引き続き登録できます。"),
        ("app-250", "APP-2.5.0", "app", "アプリ2.5.0では新しい認証方式を追加しました。ローカルネットワーク権限が無効だと製品を検出できません。"),
        ("hub-3", "HUB-FW-3", "network", "ホームハブ3では最大20台の製品を管理し、ルーター再起動後の自動再接続に対応します。"),
        ("hub-4", "HUB-FW-4", "network", "ホームハブ4ではWPA3と複数住居の切替えに対応します。旧ハブからの移行には再登録が必要です。"),
    ]
    return build_simple_family(family="firmware", title="更新履歴", filename="firmware-release-notes-2026.pdf", category="更新情報", document_type="release_note", rows=rows)


def build_compatibility() -> list[dict[str, Any]]:
    rows = [
        ("ios18", "COMPAT-IOS18", "app", "iOS 18ではアプリ2.4.0以降を利用します。ローカルネットワークとBluetoothの権限を許可しないと製品登録を開始できません。"),
        ("android15", "COMPAT-ANDROID15", "app", "Android 15では近くのデバイス権限と通知権限を個別に設定します。位置情報を常時許可する必要はありません。"),
        ("router-wpa3", "COMPAT-WPA3", "network", "WPA3を使う場合は製品側ファームウェア4以降が必要です。移行モードを使えばWPA2対応製品も同じルーターへ接続できます。"),
        ("router-5g", "COMPAT-5GHZ", "network", "WM-A410とAC-C300は2.4GHz帯だけに対応します。SSIDが5GHz専用の場合は製品登録できません。"),
        ("app240", "COMPAT-APP240", "app", "アプリ2.4.0はファームウェア2から4の製品を操作できます。ファームウェア5の一部機能は表示されません。"),
        ("app250", "COMPAT-APP250", "app", "アプリ2.5.0は新認証へ対応します。ファームウェア2の製品は初回登録時に追加確認が必要です。"),
        ("wm-a410", "COMPAT-WM-A410", "washer", "WM-A410はアプリ2.3.0以降、2.4GHz無線LAN、iOS 16以降またはAndroid 12以降で利用できます。"),
        ("wm-a410s", "COMPAT-WM-A410S", "washer", "WM-A410SはWM-A410と同じアプリを使えますが、交換部品と更新ファイルは共通ではありません。"),
        ("ac-c300", "COMPAT-AC-C300", "air_conditioner", "AC-C300はホームハブなしでも外出先操作できます。企業向け認証の無線LANには対応しません。"),
        ("rf-d510", "COMPAT-RF-D510", "refrigerator", "RF-D510の扉通知はアプリ2.4.0以降で利用できます。旧アプリでは温度履歴だけを表示します。"),
        ("tv-g800", "COMPAT-TV-G800", "television", "TV-G800はBluetoothヘッドホンへ接続できますが、同時に2台へ音声を出力できません。"),
        ("hub-old", "COMPAT-HUB2", "network", "ホームハブ2はファームウェア4の製品を登録できますが、WPA3と複数住居には対応しません。"),
        ("voice-a", "COMPAT-VOICE-A", "app", "音声アシスタントAではエアコンと照明の操作に対応します。洗濯機の運転開始は安全上の理由で行えません。"),
        ("voice-b", "COMPAT-VOICE-B", "app", "音声アシスタントBではテレビとエアコンを操作できます。冷蔵庫の扉状態は読み上げません。"),
        ("bluetooth", "COMPAT-BT5", "network", "VC-F710とTV-G800はBluetooth 5に対応しますが、家電の無線LAN登録をBluetoothだけで完了することはできません。"),
    ]
    return build_simple_family(family="compat", title="動作環境・互換性一覧", filename="compatibility-2026.pdf", category="互換性", document_type="compatibility", rows=rows)


def build_maintenance() -> list[dict[str, Any]]:
    rows = [
        ("wm-filter", "CARE-WM-FILTER", "washer", "給水口フィルターは半年ごとに確認し、砂やさびを歯ブラシで除きます。外す前に蛇口を閉めます。"),
        ("wm-drum", "CARE-WM-DRUM", "washer", "月に一度は槽洗浄コースを実行し、終了後は扉と洗剤ケースを開けて乾燥させます。"),
        ("dryer-filter", "CARE-DR-FILTER", "dryer", "乾燥フィルターは運転ごとに清掃し、月に一度は奥の吸気口のほこりも取り除きます。"),
        ("dryer-duct", "CARE-DR-DUCT", "dryer", "排気ダクトは半年ごとに外して詰まりを確認します。つぶれたダクトは伸ばさず交換します。"),
        ("ac-filter", "CARE-AC-FILTER", "air_conditioner", "エアコンのフィルターは2週間ごとに清掃します。自動清掃機能があってもダストボックスのごみは捨てます。"),
        ("ac-drain", "CARE-AC-DRAIN", "air_conditioner", "冷房期の前にドレンホース出口が土や虫で塞がれていないことを確認します。内部へ棒を差し込みません。"),
        ("rf-coil", "CARE-RF-COIL", "refrigerator", "冷蔵庫の背面と側面にほこりをためず、放熱スペースを確保します。電源を抜いてから清掃します。"),
        ("rf-ice", "CARE-RF-ICE", "refrigerator", "給水タンクと浄水フィルターを週に一度水洗いし、塩素系洗剤は使用しません。"),
        ("oven-steam", "CARE-OV-STEAM", "oven", "スチーム使用後は給水タンクを空にし、クエン酸洗浄の通知が出たら専用コースを実行します。"),
        ("oven-cavity", "CARE-OV-CAVITY", "oven", "庫内が冷えてから飛び散った油を拭き取ります。ヒーターへ洗剤を直接吹き付けません。"),
        ("vc-brush", "CARE-VC-BRUSH", "vacuum", "回転ブラシの髪や糸を週に一度取り除き、軸受けへごみが入っていないことを確認します。"),
        ("vc-battery", "CARE-VC-BATTERY", "vacuum", "長期間使わない場合も3か月に一度充電し、高温になる車内へバッテリーを放置しません。"),
        ("tv-screen", "CARE-TV-SCREEN", "television", "画面は柔らかい乾いた布で拭き、アルコールやガラス洗剤を使用しません。"),
        ("tv-vent", "CARE-TV-VENT", "television", "背面の通風孔を月に一度確認し、掃除機を弱く当ててほこりを除きます。"),
        ("app-account", "CARE-APP-ACCOUNT", "app", "譲渡や廃棄の前にアプリから製品登録を解除し、本体のネットワーク設定を初期化します。"),
    ]
    return build_simple_family(family="maintenance", title="お手入れガイド", filename="maintenance-guide-2026.pdf", category="手入れ", document_type="guide", rows=rows)


def build_installation() -> list[dict[str, Any]]:
    rows = [
        ("wm-level", "INSTALL-WM-LEVEL", "washer", "洗濯機は水平器を使って脚を調整し、対角を押してがたつかないことを確認します。"),
        ("wm-drain", "INSTALL-WM-DRAIN", "washer", "排水ホースは途中で高く持ち上げず、つぶれや逆勾配がない状態で排水口へ接続します。"),
        ("dryer-vent", "INSTALL-DR-VENT", "dryer", "乾燥機の排気ダクトは指定径を使い、曲げ回数と全長を設置基準以内に収めます。"),
        ("dryer-stack", "INSTALL-DR-STACK", "dryer", "洗濯機の上へ乾燥機を設置する場合は指定の架台を使い、壁へ転倒防止金具を固定します。"),
        ("ac-wall", "INSTALL-AC-WALL", "air_conditioner", "室内機は壁の強度を確認し、左右と上部に指定の吸気スペースを確保します。"),
        ("ac-drain", "INSTALL-AC-DRAIN", "air_conditioner", "ドレンホースは屋外へ下り勾配を付け、先端を水たまりや土の中へ入れません。"),
        ("rf-clearance", "INSTALL-RF-CLEAR", "refrigerator", "冷蔵庫は上部と側面の放熱距離を確保し、扉を開けられる壁との間隔も確認します。"),
        ("rf-level", "INSTALL-RF-LEVEL", "refrigerator", "前脚を調整して本体を安定させ、扉が自然に閉まるわずかな後傾を付けます。"),
        ("oven-power", "INSTALL-OV-POWER", "oven", "オーブンは単独回路のコンセントを使い、延長コードやたこ足配線を使用しません。"),
        ("oven-clearance", "INSTALL-OV-CLEAR", "oven", "上面と背面に放熱スペースを取り、蒸気が棚板へ直接当たらない位置へ設置します。"),
        ("vc-charge", "INSTALL-VC-CHARGE", "vacuum", "充電台は直射日光と水気を避け、付属ねじで壁の下地へ固定します。"),
        ("tv-wall", "INSTALL-TV-WALL", "television", "壁掛けは機種に合う金具を使い、壁の材質と耐荷重を施工業者が確認します。"),
        ("tv-stand", "INSTALL-TV-STAND", "television", "テレビ台は本体より広く水平なものを使い、付属ベルトで壁または台へ転倒防止固定します。"),
        ("router-place", "INSTALL-ROUTER", "network", "ルーターは家電との間に金属製家具や水槽が少ない場所へ置き、床へ直置きしません。"),
        ("hub-place", "INSTALL-HUB", "network", "ホームハブはルーターから10m以内を目安に置き、電子レンジのすぐ横を避けます。"),
    ]
    return build_simple_family(family="installation", title="設置工事ガイド", filename="installation-guide-2026.pdf", category="設置", document_type="guide", rows=rows)


def build_faq() -> list[dict[str, Any]]:
    rows = [
        ("wm-odor", "FAQ-WM-ODOR", "washer", "洗濯槽からにおいがする場合は、洗剤量を減らし、槽洗浄と排水フィルター清掃を行います。故障とは限りません。"),
        ("wm-vibration", "FAQ-WM-VIB", "washer", "脱水時の振動が大きい場合は、衣類の偏り、輸送用固定ボルト、床の水平を確認します。"),
        ("dryer-time", "FAQ-DR-TIME", "dryer", "乾燥時間が長い場合はフィルター、衣類量、室温、排気ダクトを確認します。"),
        ("ac-smell", "FAQ-AC-SMELL", "air_conditioner", "運転開始時のにおいはフィルターや熱交換器の汚れが原因になることがあります。焦げ臭い場合は使用を中止します。"),
        ("ac-noise", "FAQ-AC-NOISE", "air_conditioner", "停止後の水の流れる音や樹脂のきしみ音は温度変化で発生します。連続する金属音は点検対象です。"),
        ("fridge-frost", "FAQ-RF-FROST", "refrigerator", "冷凍室に霜が増える場合は、食品の挟まりと扉パッキンを確認します。扉を頻繁に開けた直後だけなら異常ではありません。"),
        ("fridge-hot", "FAQ-RF-HOT", "refrigerator", "冷蔵庫の側面が熱くなるのは放熱のためです。手で触れられないほどの高温や焦げ臭さがある場合は電源を抜きます。"),
        ("oven-smoke", "FAQ-OV-SMOKE", "oven", "初回運転時の少量の煙は製造時の油分による場合があります。食品残りが燃えている場合は清掃します。"),
        ("oven-spark", "FAQ-OV-SPARK", "oven", "電子レンジ運転で火花が出た場合は金属容器やアルミ箔を取り除き、庫内の汚れを確認します。"),
        ("vacuum-short", "FAQ-VC-SHORT", "vacuum", "運転時間が短い場合は強モードの使用、低温、フィルター詰まり、バッテリー劣化を確認します。"),
        ("tv-delay", "FAQ-TV-DELAY", "television", "Bluetooth音声の遅延は音声モードと接続機器で変わります。低遅延モードを選び、映像補正を減らします。"),
        ("tv-black", "FAQ-TV-BLACK", "television", "音は出るが画面が黒い場合は入力切替と省電力設定を確認します。画面を強く押しません。"),
        ("app-login", "FAQ-APP-LOGIN", "app", "アプリへログインできない場合はメールアドレス、端末時刻、認証メールの有効期限を確認します。"),
        ("app-offline", "FAQ-APP-OFFLINE", "app", "製品がオフライン表示でも通知が届く場合は表示キャッシュの可能性があります。製品登録をすぐ削除せずアプリを再起動します。"),
        ("noise-night", "FAQ-NOISE-NIGHT", "washer", "夜間に洗濯機の作動音が響く場合は、防振脚、壁との接触、予約運転の時間帯を確認します。"),
    ]
    return build_simple_family(family="faq", title="よくある質問", filename="faq-2026.pdf", category="FAQ", document_type="faq", rows=rows)


def build_context_family(
    *, family: str, title: str, filename: str,
    topics: list[tuple[str, str, list[str]]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for parent_slug, product_category, chunks in topics:
        parent_id = f"{family}-{parent_slug}"
        for order, body in enumerate(chunks, start=1):
            records.append(document(
                id=f"{parent_id}-{order}", family=family, title=title,
                filename=filename, category="サポート規定", body=body,
                identifiers=[parent_slug.upper()], parent_id=parent_id,
                chunk_order=order, document_type="policy",
                product_category=product_category,
            ))
    return records


def build_warranty_context() -> list[dict[str, Any]]:
    return build_context_family(
        family="warranty-context", title="保証判定ガイド", filename="warranty-policy-2026.pdf",
        topics=[
            ("wm-a410", "washer", [
                "WM-A410は購入から12か月以内に製造上の不具合が確認された場合、無償修理または同等品への交換対象になります。",
                "申請には製造番号、購入日を確認できる書類、表示されたエラー、実施済みの確認手順を添えます。",
                "給水口の未清掃、排水ホースの誤設置、異物混入、業務利用による故障は対象外です。ただし安全上の回収対象は保証期間外でも別に対応します。",
            ]),
            ("ac-c300", "air_conditioner", [
                "AC-C300の冷媒回路や制御基板に製造上の不具合がある場合は、購入から5年間の特別保証を適用します。",
                "施工記録、製造番号、故障コード、配管長、点検時の圧力を保証申請へ記載します。",
                "指定外施工、移設時の配管再利用、落雷や浸水による故障は特別保証の対象外です。",
            ]),
            ("rf-d510", "refrigerator", [
                "RF-D510の圧縮機と冷却器は購入から5年間、それ以外の部品は1年間を無償修理期間とします。",
                "冷却不良では庫内温度、設置間隔、扉の開閉状態、製造番号を確認して申請します。",
                "食品の詰め込みや扉の閉め忘れだけが原因の場合は保証修理の対象外です。",
            ]),
            ("ov-e600", "oven", [
                "OV-E600は購入から12か月以内のヒーター、センサー、制御基板の製造不良を無償修理します。",
                "エラー履歴、使用した加熱モード、容器、庫内写真を申請へ添付します。",
                "金属容器の誤使用、清掃不足による発煙、業務用途での連続運転は対象外です。",
            ]),
            ("tv-g800", "television", [
                "TV-G800は購入から12か月以内の基板とパネルの製造不良を保証します。",
                "画面症状の写真、入力機器を外した結果、製造番号、購入日を記録します。",
                "外部からの衝撃、壁掛け施工不良、長時間の静止画による焼き付きは対象外です。",
            ]),
        ],
    )


def build_safety_context() -> list[dict[str, Any]]:
    return build_context_family(
        family="safety-context", title="安全対応ガイド", filename="safety-response-2026.pdf",
        topics=[
            ("recall-wm-a401", "washer", [
                "対象製造番号のWM-A401では電源部品を無償交換する回収対応を行います。使用を停止し電源プラグを抜きます。",
                "型番、製造番号、設置先、連絡先を確認し、回収受付へ登録します。",
                "通常保証が終了していても回収対象なら無償です。対象外の製造番号へ予防交換は行いません。",
            ]),
            ("overheating-dryer", "dryer", [
                "乾燥機から焦げ臭さや煙が出た場合は運転を停止し、可能なら電源プラグを抜きます。",
                "煙の有無、停止前の運転時間、フィルター状態、周囲への延焼がないことを確認します。",
                "通常の温風のにおいだけで煙や異常発熱がない場合は、冷却後にフィルターを点検します。",
            ]),
            ("gas-oven", "oven", [
                "オーブンから火花が出た場合は加熱を停止し、扉を開けず電源を切ります。",
                "庫内が冷えてから金属片、アルミ箔、焦げた食品、導波板の損傷を確認します。",
                "初回運転の少量の煙だけで火花がない場合は、換気しながら空焼き手順を続けられます。",
            ]),
            ("battery-vacuum", "vacuum", [
                "掃除機のバッテリーが膨らんだ場合は充電と使用を中止し、端子へ触れないよう保管します。",
                "型番、製造番号、膨らみの写真、落下や水濡れの有無を確認して回収を手配します。",
                "単に運転時間が短いだけで膨らみや発熱がない場合は、安全回収ではなく劣化診断を行います。",
            ]),
            ("tipover-tv", "television", [
                "テレビが傾いた、または転倒した場合は使用を中止し、画面と電源コードへ触れず安全を確保します。",
                "壁掛け金具、スタンド、固定ベルト、壁の損傷を写真で確認し、施工担当へ連絡します。",
                "地震後に外観上の異常がなく固定部も緩んでいない場合は、電源コードを確認してから使用を再開できます。",
            ]),
        ],
    )


def query(
    id: str, split: str, category: str, text: str, relevance: dict[str, int],
    *, mode: str | None = None, filters: dict[str, Any] | None = None,
    required_context_ids: list[str] | None = None,
    expected_ids: list[str] | None = None,
    forbidden_ids: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": id, "split": split, "category": category, "case_group": id,
        "query": text, "relevance": relevance, "mode": mode,
        "filters": filters or {}, "required_context_ids": required_context_ids or [],
        "expected_ids": expected_ids or [], "forbidden_ids": forbidden_ids or [],
    }


def build_queries() -> list[dict[str, Any]]:
    queries: list[dict[str, Any]] = []
    groups = {
        "semantic": {
            "dev": [
                ("更新後に家電がアプリから消えたが、登録し直したら使えるようになった事例", "support-connect-01"),
                ("給水が遅かったが部品を替えずに入口の砂を取って直った修理", "repair-case-01"),
                ("乾燥時間が延びないよう毎回掃除する場所", "manual-dryer-filter"),
                ("外からエアコンを操作するときの再接続を改善した更新", "firmware-ac-c300-3"),
                ("新しいiPhoneで家電を探すために許可する項目", "compat-ios18"),
                ("洗濯機へ水が入りにくくなる前に砂やさびを取る手入れ", "maintenance-wm-filter"),
                ("エアコンを壁へ付けるときに必要な強度と吸気空間", "installation-ac-wall"),
                ("夜間の洗濯音が家に響くときの確認方法", "faq-noise-night"),
                ("床の種類に応じて吸う強さを自動で変える掃除機", "product-vc-f710"),
                ("テレビの動画サービスで認証に失敗したときのコード", "error-tv-g800-e31"),
            ],
            "test": [
                ("更新は終わったのにスマートフォンから操作できない洗濯機の事例", "support-connect-03"),
                ("乾燥機を掃除しても熱で停止し、交換部品待ちになった修理", "repair-case-03"),
                ("洗濯機に水が入らないとき蛇口から順に調べる手順", "manual-wm-water"),
                ("WPA3のルーターへエアコンをつなぐための更新", "firmware-ac-c300-4"),
                ("新しい暗号方式と古い家電を同じ無線LANで使う条件", "compat-router-wpa3"),
                ("冷房前にエアコンのほこりを取る頻度", "maintenance-ac-filter"),
                ("洗濯機の水を流すホースを高くしない設置方法", "installation-wm-drain"),
                ("冷凍室に霜が増えたとき扉の隙間を確認する案内", "faq-fridge-frost"),
                ("扉を閉め忘れたときスマートフォンへ知らせる大型冷蔵庫", "product-rf-d510"),
                ("掃除機のブラシに髪が絡んで止まったときのコード", "error-vc-f710-e31"),
            ],
        },
        "lexical": {
            "dev": [("WM-A410S", "product-wm-a410s"), ("WM-A410 E24", "error-wm-a410-e24"), ("FW-TV-G800-5", "firmware-tv-g800-5"), ("COMPAT-APP240", "compat-app240"), ("CARE-RF-COIL", "maintenance-rf-coil"), ("INSTALL-TV-WALL", "installation-tv-wall"), ("FAQ-APP-LOGIN", "faq-app-login"), ("MANUAL-OV-STEAM", "manual-oven-steam"), ("CASE-REPAIR-05", "repair-case-05"), ("CASE-CONNECT-05", "support-connect-05")],
            "test": [("WM-A410", "product-wm-a410"), ("WM-A410 E42", "error-wm-a410-e42"), ("FW-WM-A410-4", "firmware-wm-a410-4"), ("COMPAT-APP250", "compat-app250"), ("CARE-VC-BRUSH", "maintenance-vc-brush"), ("INSTALL-RF-CLEAR", "installation-rf-clearance"), ("FAQ-WM-ODOR", "faq-wm-odor"), ("MANUAL-TV-NET", "manual-tv-network"), ("CASE-REPAIR-07", "repair-case-07"), ("CASE-CONNECT-14", "support-connect-14")],
        },
        "mixed": {
            "dev": [("AC-C300のE24で室外機と通信できない", "error-ac-c300-e24"), ("AC-C330は寒い地域でどの程度暖房できる製品か", "product-ac-c330"), ("CASE-CONNECT-07で外出先操作が使えない原因", "support-connect-07"), ("CASE-REPAIR-09の排水エラーを直した方法", "repair-case-09"), ("VC-F710で清掃履歴の同期を改善した更新", "firmware-vc-f710-3"), ("Android 15で近くの家電を見つける権限", "compat-android15"), ("OV-E600の蒸気が弱くならないための水あか清掃", "maintenance-oven-steam"), ("DR-B220の排気ダクトの長さと曲げ方", "installation-dryer-vent"), ("TV-G800のBluetooth音声が映像より遅れる", "faq-tv-delay"), ("AC-C300を2.4GHzへ登録するボタン操作", "manual-ac-pairing")],
            "test": [("WM-A410でE42が出たときの給水エラーの対処", "error-wm-a410-e42"), ("WM-A410をスマートフォンから予約運転できるか", "product-wm-a410"), ("CASE-CONNECT-03で更新後も接続できない経緯", "support-connect-03"), ("CASE-REPAIR-11で給水弁の交換が未完了の理由", "repair-case-11"), ("WM-A410の予約運転と再接続を改善した更新", "firmware-wm-a410-3"), ("WM-A410が5GHzだけのSSIDへ接続できない理由", "compat-router-5g"), ("WM-A410の槽を月に一度洗浄する手順", "maintenance-wm-drum"), ("WM-A410の振動を抑える水平調整", "installation-wm-level"), ("通知は届くのにアプリではオフラインと出る", "faq-app-offline"), ("WM-A410のE24で排水できないときの確認箇所", "manual-wm-drain")],
        },
    }
    prefixes = {"semantic": "sem", "lexical": "lex", "mixed": "mix"}
    for category, sets in groups.items():
        for split, rows in sets.items():
            marker = "d" if split == "dev" else "t"
            for index, (text, target) in enumerate(rows, start=1):
                queries.append(query(f"{prefixes[category]}-{marker}{index:02d}", split, category, text, {target: 3}))

    negation = {
        "dev": [
            ("更新後に再登録して接続できるようになった事例", "support-connect-01", "support-connect-03"),
            ("本体は接続済みだが権限不足でアプリ操作できない事例", "support-connect-02", "support-connect-06"),
            ("ルーター再起動で通知が届くようになった冷蔵庫", "support-connect-05", "support-connect-12"),
            ("接続はできるが通知だけ遅れていた事例", "support-connect-06", "support-connect-03"),
            ("新しいSSIDへ登録しても外出先操作できない事例", "support-connect-07", "support-connect-13"),
            ("アプリの再インストールで接続が回復した事例", "support-connect-08", "support-connect-09"),
            ("Bluetoothでは見えるがクラウド同期できない事例", "support-connect-09", "support-connect-08"),
            ("更新を再適用して接続できる状態へ戻ったテレビ", "support-connect-10", "support-connect-14"),
            ("5GHz専用SSIDのため洗濯機を登録できない事例", "support-connect-11", "support-connect-15"),
            ("通知は送れるのにアプリ表示だけ直らない冷蔵庫", "support-connect-12", "support-connect-05"),
        ],
        "test": [
            ("ソフトウェアを新しくした後も、あらゆる再接続を試して直らなかった事例", "support-connect-03", "support-connect-13"),
            ("更新をまだ行っておらず新しい認証へ接続できない事例", "support-connect-04", "support-connect-03"),
            ("更新後に再起動だけでアプリ操作を再開できた事例", "support-connect-13", "support-connect-03"),
            ("スマートフォン交換後も新端末へ接続できない事例", "support-connect-14", "support-connect-15"),
            ("旧ファームウェアだが現在は接続できている事例", "support-connect-15", "support-connect-04"),
            ("清掃だけで乾燥機の過熱停止が解消した修理", "repair-case-02", "repair-case-03"),
            ("清掃しても過熱停止が続き部品交換待ちの修理", "repair-case-03", "repair-case-02"),
            ("冷房が弱く清掃後も改善しなかったエアコン", "repair-case-08", "repair-case-15"),
            ("画面の縦線が直らずパネル交換待ちのテレビ", "repair-case-14", "repair-case-07"),
            ("バッテリー交換で運転時間が元に戻った掃除機", "repair-case-13", "repair-case-06"),
        ],
    }
    for split, rows in negation.items():
        marker = "d" if split == "dev" else "t"
        for index, (text, target, forbidden) in enumerate(rows, start=1):
            queries.append(query(f"neg-{marker}{index:02d}", split, "negation_exception", text, {target: 3}, forbidden_ids=[forbidden]))

    contexts = {
        "dev": [("AC-C300の特別保証の条件と対象外", "warranty-context-ac-c300"), ("RF-D510の部品別保証期間と対象外", "warranty-context-rf-d510"), ("OV-E600の無償修理に必要な情報と対象外", "warranty-context-ov-e600"), ("TV-G800の保証条件と対象外になる破損", "warranty-context-tv-g800"), ("WM-A401の回収対象と保証期間外の扱い", "safety-context-recall-wm-a401")],
        "test": [("WM-A410の無償交換が認められる条件と、対象外になる場合", "warranty-context-wm-a410"), ("乾燥機から焦げ臭さがしたときの停止条件と通常のにおいとの違い", "safety-context-overheating-dryer"), ("オーブンで火花が出たときの対応と初回の煙だけの場合", "safety-context-gas-oven"), ("掃除機のバッテリー膨張時の回収と単なる劣化の違い", "safety-context-battery-vacuum"), ("テレビ転倒時の確認と地震後に使用再開できる条件", "safety-context-tipover-tv")],
    }
    for split, rows in contexts.items():
        marker = "d" if split == "dev" else "t"
        for index, (text, parent) in enumerate(rows, start=1):
            ids = [f"{parent}-{order}" for order in range(1, 4)]
            queries.append(query(f"ctx-{marker}{index:02d}", split, "context", text, {ids[0]: 1, ids[1]: 1, ids[2]: 3}, required_context_ids=ids))

    constraints = {
        "dev": [
            ("WM-A410-E24", "exact", {}, ["error-wm-a410-e24"]),
            ("AC-C300-E24", "exact", {}, ["error-ac-c300-e24"]),
            ("ルーター交換後も外出先操作できない事例", "hybrid", {"document_type": "support_case"}, ["support-connect-07"]),
            ("ブラシを清掃してもE31が再発した訪問修理", "hybrid", {"document_type": "repair_case"}, ["repair-case-06"]),
            ("回転ブラシに絡んだ髪や糸を取り除く手順", "hybrid", {"document_type": "manual"}, ["manual-vacuum-brush"]),
        ],
        "test": [
            ("WM-A410-E42", "exact", {}, ["error-wm-a410-e42"]),
            ("RF-D510-E17", "exact", {}, ["error-rf-d510-e17"]),
            ("更新後、再登録と再起動でも接続できない事例", "hybrid", {"document_type": "support_case"}, ["support-connect-03"]),
            ("給水弁の交換部品を手配した未完了の訪問修理", "hybrid", {"document_type": "repair_case"}, ["repair-case-11"]),
            ("洗濯機に水が入らないときの確認手順", "hybrid", {"document_type": "manual"}, ["manual-wm-water"]),
        ],
    }
    for split, rows in constraints.items():
        marker = "d" if split == "dev" else "t"
        for index, (text, mode, filters, expected) in enumerate(rows, start=1):
            queries.append(query(f"con-{marker}{index:02d}", split, "constraint", text, {}, mode=mode, filters=filters, expected_ids=expected))
    return queries


def main() -> None:
    documents = [
        *build_products(), *build_error_codes(), *build_connectivity_cases(),
        *build_repair_cases(), *build_manuals(), *build_firmware_notes(),
        *build_compatibility(), *build_maintenance(), *build_installation(),
        *build_faq(), *build_warranty_context(), *build_safety_context(),
    ]
    queries = build_queries()
    if len(documents) != 180:
        raise SystemExit(f"expected 180 documents, got {len(documents)}")
    if len(queries) != 100:
        raise SystemExit(f"expected 100 queries, got {len(queries)}")
    CORPUS_PATH.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in documents), encoding="utf-8")
    QUERIES_PATH.write_text(json.dumps(queries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(documents)} documents and {len(queries)} queries")


if __name__ == "__main__":
    main()
