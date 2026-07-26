#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "data" / "corpus.jsonl"
QUERIES_PATH = ROOT / "data" / "evaluation_queries.json"


def document(
    *,
    id: str,
    family: str,
    title: str,
    filename: str,
    category: str,
    body: str,
    identifiers: list[str] | None = None,
    parent_id: str | None = None,
    chunk_order: int | None = None,
    document_type: str,
    customer_age: int | None = None,
    amount_yen: int | None = None,
    case_outcome: str | None = None,
) -> dict[str, Any]:
    return {
        "id": id,
        "family": family,
        "title": title,
        "filename": filename,
        "category": category,
        "page_start": 1,
        "identifiers": identifiers or [],
        "parent_id": parent_id,
        "chunk_order": chunk_order,
        "document_type": document_type,
        "customer_age": customer_age,
        "amount_yen": amount_yen,
        "case_outcome": case_outcome,
        "synthetic": True,
        "body": body,
    }


def build_rules() -> list[dict[str, Any]]:
    rows = [
        ("019", "第19条", "高齢顧客へ複雑な金融商品を勧誘する場合は、商品のリスク、手数料、途中解約時の取扱いを説明し、理解度の確認記録を5年間保存します。75歳以上では管理者の事前承認も必要です。"),
        ("019-2", "第19条の2", "第19条の2は、高齢顧客が自ら継続購入を申し出た場合の確認手順を定めます。前回購入から6か月以内でも、理解度と資産状況を改めて確認しなければなりません。"),
        ("020", "第20条", "電話で商品を案内した顧客が明確に断った場合、同じ商品を30日以内に再勧誘してはなりません。資料送付だけを希望した顧客への説明は、同意を得た範囲に限ります。"),
        ("021", "第21条", "訪問による勧誘は午前9時から午後7時までとし、顧客から別の時間帯を明示的に指定された場合だけ、その記録を残して対応できます。"),
        ("022", "第22条", "契約締結前交付書面は、顧客が内容を確認できる時点で交付します。電子交付を利用する場合は、閲覧可能になった日時を記録します。"),
        ("023", "第23条", "元本保証と誤認させる表現を広告へ使用してはなりません。過去の運用実績を示す場合も、将来の成果を保証しない旨を同じ画面へ表示します。"),
        ("024", "第24条", "苦情を受け付けた担当者は、翌営業日までに顧客対応管理部へ連携します。重大な損失が疑われる場合は、金額が未確定でも直ちに報告します。"),
        ("025", "第25条", "顧客との面談記録は契約終了後7年間保存します。録音データを廃棄しても、説明項目と確認結果を記載した記録は保存対象です。"),
        ("026", "第26条", "代理人から注文を受ける場合は、代理権の範囲と有効期限を確認します。本人確認が完了していても、対象商品の取引権限がなければ受注できません。"),
        ("027", "第27条", "未成年者口座では法定代理人の同意を確認します。積立額の変更と高リスク商品の追加購入には、都度の同意記録が必要です。"),
        ("028", "第28条", "外国語で説明する場合は、顧客が理解できる言語の資料を用意します。通訳者を介した場合は、通訳者の氏名と説明日時を記録します。"),
        ("029", "第29条", "手数料の変更は適用開始日の30日前までに通知します。既存契約へ遡って新しい料率を適用することはできません。"),
        ("030", "第30条", "システム障害で注文時刻を確定できない場合は、受信ログと顧客申告を照合します。推測した時刻だけで約定訂正を行ってはなりません。"),
        ("031", "第31条", "利益相反のおそれがある商品を提案する場合は、販売側が受け取る報酬と代替商品の有無を説明します。説明記録は商品別に残します。"),
        ("032", "第32条", "顧客情報を検索目的で利用する場合は、業務上必要な範囲に限定します。検証環境へ複製するときは識別情報を仮名化します。"),
    ]
    return [
        document(
            id=f"rule-{slug}",
            family="rules",
            title="顧客保護規程 2025年版",
            filename="customer-protection-rules-2025.pdf",
            category="規程",
            body=body,
            identifiers=[label, f"RULE-{slug.upper()}"],
            document_type="rule",
        )
        for slug, label, body in rows
    ]


def build_products() -> list[dict[str, Any]]:
    rows = [
        ("ALPHA-01", "国内債券を中心に運用する安定型商品です。申込単位は10万円で、標準的な換金期間は3営業日です。金利上昇時には基準価額が下落する可能性があります。"),
        ("ALPHA-10", "海外株式を中心に運用する成長型商品です。申込単位は10万円で、為替変動と株価変動による元本割れの可能性があります。換金には7営業日かかります。"),
        ("ALPHA-07", "為替ヘッジ付きの外国債券商品です。外貨資産へ投資しますが、原則として為替変動の影響を抑える運用を行います。換金期間は5営業日です。"),
        ("BETA-01", "国内の短期金融資産へ投資する商品です。価格変動を抑える設計ですが、元本保証ではありません。購入手数料はなく、換金期間は2営業日です。"),
        ("BETA-10", "新興国の株式と債券へ分散投資する商品です。大きな価格変動と為替変動が想定され、積極型の顧客を対象とします。"),
        ("GAMMA-02", "複数の国内REITへ投資し、賃料収入を原資とする分配を目指します。不動産市況と金利の変動により価格が下落することがあります。"),
        ("GAMMA-20", "海外REITへ投資する毎月分配型商品です。分配金が投資元本の一部払戻しとなる場合があり、為替変動の影響も受けます。"),
        ("DELTA-03", "日経平均株価に連動することを目指すインデックス商品です。指数の下落に応じて基準価額も下落し、元本は保証されません。"),
        ("DELTA-30", "日経平均株価の値動きの逆方向へ連動することを目指す商品です。長期保有では複利効果により指数の単純な逆数と乖離します。"),
        ("EPSILON-04", "物価連動国債へ投資し、物価上昇への対応を目指します。実質金利の変動や市場流動性の低下により価格が変動します。"),
        ("EPSILON-40", "金価格との連動を目指す上場商品です。金価格だけでなく、為替相場と市場価格の乖離による影響を受けます。"),
        ("OMEGA-05", "期限前償還条項を持つ仕組債です。参照指数が一定水準を下回ると償還額が元本を割り込むため、複雑商品として扱います。"),
        ("OMEGA-50", "複数銘柄を参照する期限前償還条項付き仕組債です。いずれかの銘柄が基準を下回ると損失が生じる可能性があります。"),
        ("SIGMA-06", "国内外の債券と株式を均等に配分するバランス商品です。四半期ごとに基本配分へ戻すリバランスを行います。"),
        ("SIGMA-60", "市場変動に応じて株式比率を調整するバランス商品です。急激な相場変動時には比率変更が遅れる可能性があります。"),
    ]
    return [
        document(
            id=f"product-{code.lower()}",
            family="products",
            title="取扱商品説明書 2025年版",
            filename="product-guide-2025.pdf",
            category="商品",
            body=body,
            identifiers=[code],
            document_type="product",
        )
        for code, body in rows
    ]


def build_deadlines() -> list[dict[str, Any]]:
    rows = [
        ("review-30", "通常審査", 30, "通常審査は申請受付から30日以内に一次判定を完了します。追加資料を依頼してから受領するまでの期間は、審査日数へ含めません。"),
        ("review-60", "特別審査", 60, "複雑な取引を含む特別審査は60日以内に一次判定を完了します。通常審査の30日基準を適用してはなりません。"),
        ("retention-30", "一時ログ保存", 30, "障害調査用の一時ログは30日間保存し、調査終了後に削除します。審査期限ではなく、技術ログの保存期間です。"),
        ("notice-30", "手数料変更通知", 30, "手数料率を変更する場合は適用開始日の30日前までに顧客へ通知します。通知後30日以内に変更するという意味ではありません。"),
        ("complaint-2", "苦情一次回答", 2, "苦情を受け付けた場合は2営業日以内に一次回答し、調査継続時は次回連絡予定日を伝えます。"),
        ("refund-5", "過徴収返金", 5, "手数料の過徴収が確定した場合は5営業日以内に返金処理を開始します。投資損失の補てんとは区別して記録します。"),
        ("approval-1", "緊急承認", 1, "緊急性の高い口座制限解除は、受付当日中に管理者の承認を得ます。承認前に解除操作を行うことはできません。"),
        ("archive-365", "監査資料移管", 365, "完了した監査案件の資料は365日後に低頻度ストレージへ移管します。法定保存期間が終了するわけではありません。"),
        ("kyc-90", "本人確認更新", 90, "本人確認情報の更新依頼に回答がない場合は、90日後に一部取引を制限します。制限前に複数回の通知を行います。"),
        ("cancel-8", "契約取消受付", 8, "対象商品について契約書面受領日から8日以内の取消しを受け付けます。対象外商品には同じ期間を適用しません。"),
        ("incident-3", "障害報告", 3, "重大障害は検知から3時間以内に責任者へ第一報を行います。原因が未確定でも影響範囲を添えて報告します。"),
        ("record-7y", "面談記録保存", 2555, "面談記録は契約終了後7年間保存します。日数換算値は運用上の目安であり、廃棄日は暦日に基づいて決定します。"),
        ("appeal-14", "異議申立て", 14, "審査結果への異議申立ては通知受領後14日以内に受け付けます。追加資料がある場合は申立てと同時に提出します。"),
        ("settlement-4", "海外商品受渡し", 4, "対象となる海外商品の受渡しは原則4営業日後です。市場休業日がある場合は受渡日を繰り下げます。"),
        ("deletion-45", "退職者権限削除", 45, "退職予定者の不要な権限は最終出社日の45日前から確認し、最終出社日の終了時までに削除します。"),
    ]
    return [
        document(
            id=f"deadline-{slug}",
            family="deadlines",
            title="業務処理基準 2025年版",
            filename="operation-deadlines-2025.pdf",
            category="手順",
            body=body,
            identifiers=[label, f"DAYS-{days}"],
            document_type="procedure",
        )
        for slug, label, days, body in rows
    ]


def build_elderly_cases() -> list[dict[str, Any]]:
    rows = [
        ("01", 78, 5_000_000, "violation", "担当者は78歳の顧客へ複雑な仕組債を販売しました。元本割れの条件を十分に説明せず、家族同席も提案せず、管理者承認の記録もなかったため不適切な勧誘と判断されました。"),
        ("02", 76, 4_000_000, "non_violation", "76歳の顧客から高リスク商品の購入希望がありましたが、理解が十分でないと判断して勧誘を行いませんでした。後日、家族同席で低リスク商品を説明しており、不適切勧誘には該当しません。"),
        ("03", 82, 3_000_000, "violation", "82歳の顧客へ投資信託を販売した面談には家族が同席しました。しかし、損失リスクをどのように確認したか記録がなく、事後検証できない点が問題となりました。"),
        ("04", 74, 8_000_000, "non_violation", "74歳の顧客へ仕組債の説明を行いました。管理者承認の年齢基準には達していませんが、商品が複雑なため家族同席を提案し、顧客が購入を見送った記録を残しました。"),
        ("05", 79, 7_000_000, "violation", "79歳の顧客が安定運用を希望していたにもかかわらず、担当者は値動きの大きい海外株式商品を販売しました。意向との不一致と説明不足が確認されました。"),
        ("06", 80, 2_000_000, "non_violation", "80歳の顧客へ国内債券商品を案内し、家族同席で価格変動と換金期間を説明しました。理解度確認と管理者承認が記録され、手続上の問題は認められませんでした。"),
        ("07", 77, 6_000_000, "violation", "77歳の顧客に対し、担当者は期限前償還だけを強調して仕組債を販売しました。参照指数下落時の損失を説明しておらず、説明内容が不十分でした。"),
        ("08", 81, 6_000_000, "non_violation", "81歳の顧客が以前から保有する同一商品の継続購入を希望しました。理解度を再確認し、管理者承認と家族への連絡を行ったうえで受注しました。"),
        ("09", 73, 5_500_000, "violation", "73歳の顧客へ高リスク商品を販売しました。年齢基準未満でしたが、投資経験がなく生活資金が中心であり、適合性確認が不十分と判断されました。"),
        ("10", 85, 1_000_000, "non_violation", "85歳の顧客から商品の問い合わせを受けましたが、担当者は一般情報の提供だけを行い、購入を勧めませんでした。問い合わせ記録にも勧誘を行っていないことを残しました。"),
        ("11", 75, 10_000_000, "violation", "75歳の顧客への販売で管理者承認はありましたが、承認後に投資金額が1000万円へ変更されていました。変更後の資産状況を確認しなかったため手続違反となりました。"),
        ("12", 83, 4_500_000, "non_violation", "83歳の顧客へ複数回説明し、最終面談では家族と管理者が同席しました。顧客はリスクを自分の言葉で説明でき、購入額も余裕資金の範囲でした。"),
        ("13", 72, 9_000_000, "violation", "72歳の顧客へ短期間に複数の商品を乗り換えさせ、多額の手数料が発生しました。年齢ではなく、取引頻度と顧客利益の観点から不適切と判断されました。"),
        ("14", 88, 500_000, "non_violation", "88歳の顧客の定期預金満期手続を支援しました。投資商品の案内は行わず、本人の依頼どおり普通預金へ入金したため勧誘事例ではありません。"),
        ("15", 78, 5_500_000, "violation", "78歳の顧客へ外貨建て商品を販売した際、為替手数料は説明しましたが為替差損の可能性を説明していませんでした。重要なリスク説明の欠落が問題となりました。"),
    ]
    return [
        document(
            id=f"elderly-case-{slug}",
            family="elderly-cases",
            title="顧客対応事例集 2024年度",
            filename="customer-cases-2024.pdf",
            category="事例",
            body=body,
            identifiers=[f"CASE-ELDERLY-{slug}"],
            document_type="case",
            customer_age=age,
            amount_yen=amount,
            case_outcome=outcome,
        )
        for slug, age, amount, outcome, body in rows
    ]


def build_compensation_cases() -> list[dict[str, Any]]:
    rows = [
        ("01", 5_000_000, "violation", "営業部門は重要顧客との関係維持を目的に、投資損失500万円を業務委託費の名目で支払いました。名目にかかわらず実質的な損失補てんに当たると判断されました。"),
        ("02", 500_000, "non_violation", "システム障害で二重徴収した手数料50万円を顧客へ返還しました。過徴収分の返金であり、投資判断による損失を穴埋めするものではありません。"),
        ("03", 1_200_000, "violation", "価格下落への苦情を収束させるため、担当者が顧客へ120万円相当の商品券を渡しました。謝罪名目でも損失額に連動した利益提供であり問題となりました。"),
        ("04", 80_000, "non_violation", "約定訂正により本来徴収すべきでなかった手数料8万円を返金しました。訂正根拠と計算過程が残されており、損失補てんには該当しません。"),
        ("05", 3_000_000, "violation", "営業担当者が顧客の含み損300万円を埋める目的で、別取引の手数料を免除しました。取引条件の変更による実質的な補てんと判断されました。"),
        ("06", 300_000, "non_violation", "災害に伴う全顧客共通の手数料減免として30万円分を免除しました。個別の投資損失と結び付かず、公開された基準に従う措置です。"),
        ("07", 7_500_000, "violation", "損失を出した顧客企業から実体のない調査業務を受託し、750万円を支払いました。役務の対価ではなく損失穴埋めが目的でした。"),
        ("08", 150_000, "non_violation", "事務遅延で発生した実費15万円を領収書に基づいて賠償しました。投資商品の価格変動とは関係がなく、範囲も実損額に限定されています。"),
        ("09", 2_000_000, "violation", "顧客の売買損200万円を担当者個人が現金で支払いました。会社経費を使っていなくても、顧客損失を補う行為は禁止対象です。"),
        ("10", 600_000, "non_violation", "誤った振込先案内により発生した送金手数料60万円を補償しました。原因調査と承認を経た事務事故の賠償として処理されています。"),
        ("11", 4_000_000, "violation", "損失のある顧客だけに将来の手数料400万円分を無償化しました。一般キャンペーンを装っていましたが対象選定が損失額に基づいていました。"),
        ("12", 200_000, "non_violation", "すべての新規顧客を対象とする公開キャンペーンで手数料20万円を上限に還元しました。投資損失の有無は対象条件ではありません。"),
        ("13", 9_000_000, "violation", "取引損失900万円を埋めるため、関連会社が顧客資産を市場価格より高く買い取りました。第三者を介しても実質的な補てんに当たります。"),
        ("14", 100_000, "non_violation", "口座閉鎖後に判明した税計算誤りについて10万円を返金しました。計算根拠を訂正した返金で、運用損失とは関係しません。"),
        ("15", 6_000_000, "violation", "顧客の損失600万円と同額を、紹介料として親族の会社へ支払いました。紹介業務の実態がなく、迂回した利益提供と認定されました。"),
    ]
    return [
        document(
            id=f"comp-case-{slug}",
            family="compensation-cases",
            title="補償判断事例集 2024年度",
            filename="compensation-cases-2024.pdf",
            category="事例",
            body=body,
            identifiers=[f"CASE-COMP-{slug}"],
            document_type="case",
            amount_yen=amount,
            case_outcome=outcome,
        )
        for slug, amount, outcome, body in rows
    ]


def build_permissions() -> list[dict[str, Any]]:
    rows = [
        ("VIEW-01", "一般担当者は監査記録を閲覧できますが、承認状態の変更と記録の削除は実行できません。コメントの追記は自分が担当する案件だけ許可されます。"),
        ("ADMIN-01", "管理者は監査記録の承認状態を変更できます。ただし、確定済み記録の本文を削除することはできず、訂正履歴を残す必要があります。"),
        ("AUDIT-01", "内部監査担当者は全部門の記録を閲覧できますが、営業部門の申請を承認できません。監査メモは内部監査担当者だけが編集できます。"),
        ("TEMP-01", "一時担当者には閲覧権限だけを付与し、顧客情報のダウンロードと一括出力を禁止します。権限は7日後に自動失効します。"),
        ("EXPORT-01", "顧客情報の一括出力は情報管理責任者の承認後に実行できます。通常の管理者権限だけでは出力を開始できません。"),
        ("DELETE-01", "保存期限を過ぎた一時ログはシステム管理者が削除できます。顧客面談記録は期限を過ぎても法務確認が完了するまで削除できません。"),
        ("APPROVE-01", "所属長は1000万円未満の取引申請を承認できます。1000万円以上はリスク管理部の追加承認が必要です。"),
        ("APPROVE-10", "リスク管理部は高額取引の追加承認を行えますが、申請者と同一人物が承認者を兼ねることはできません。"),
        ("READ-02", "外部委託先は割り当てられた匿名化データだけを閲覧できます。原本データ、氏名、契約IDへアクセスする権限はありません。"),
        ("EDIT-02", "データ品質担当者は誤記を訂正できますが、顧客の同意記録と承認結果は変更できません。訂正前の値は履歴へ保存されます。"),
        ("API-01", "検索API用サービスアカウントは公開済み文書だけを参照できます。非公開文書を含むindexへの直接検索権限は付与しません。"),
        ("API-10", "投入API用サービスアカウントは文書を登録できますが、検索結果を取得する権限はありません。用途ごとに認証情報を分離します。"),
        ("BRANCH-01", "支店担当者は自支店の案件だけを閲覧できます。本部管理者でも、調査目的が記録されていなければ他支店の顧客情報を参照できません。"),
        ("LEGAL-01", "法務担当者は係争中案件の保存期限を延長できますが、元の保存期限や作成日時を書き換えることはできません。"),
        ("GUEST-01", "研修用ゲストは架空データだけを検索できます。本番顧客データと同じ認証経路を利用せず、出力機能も無効化します。"),
    ]
    return [
        document(
            id=f"permission-{code.lower()}",
            family="permissions",
            title="業務権限一覧 2025年版",
            filename="permission-matrix-2025.pdf",
            category="権限",
            body=body,
            identifiers=[code],
            document_type="permission",
        )
        for code, body in rows
    ]


def build_context_family(
    *,
    family: str,
    title: str,
    filename: str,
    topics: list[tuple[str, list[str]]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for parent_slug, chunks in topics:
        parent_id = f"{family}-{parent_slug}"
        for index, body in enumerate(chunks, start=1):
            records.append(
                document(
                    id=f"{parent_id}-{index}",
                    family=family,
                    title=title,
                    filename=filename,
                    category="規程",
                    body=body,
                    identifiers=[parent_slug.upper()],
                    parent_id=parent_id,
                    chunk_order=index,
                    document_type="rule",
                )
            )
    return records


def build_approval_context() -> list[dict[str, Any]]:
    return build_context_family(
        family="approval-context",
        title="承認手続細則 2025年版",
        filename="approval-procedure-2025.pdf",
        topics=[
            ("elderly", [
                "75歳以上の顧客へ複雑な金融商品を勧誘する場合は、原則として管理者の事前承認を受けます。",
                "承認申請には投資経験、金融資産、購入目的、家族同席の有無、理解度確認の結果を記載します。",
                "ただし、同一商品の継続購入を顧客が自発的に申し出て、理解度を再確認できた場合は簡易承認を利用できます。承認自体が不要になるわけではありません。",
            ]),
            ("urgent", [
                "口座の不正利用が疑われる場合は、管理者承認を得て出金を停止することを原則とします。",
                "夜間など管理者へ連絡できず、資産流出のおそれが高い場合は、当番責任者が暫定停止を実行できます。",
                "暫定停止を行った場合は翌営業日の午前10時までに管理者の追認を得て、判断根拠を記録します。",
            ]),
            ("high-value", [
                "1000万円以上の高額取引は、所属長とリスク管理部による二段階承認を必要とします。",
                "金額は同一顧客が同日に行う関連取引を合算して判定し、分割注文で基準を回避してはなりません。",
                "国債の償還金を同じ国債へ再投資する場合は、商品性が変わらないことを確認したうえでリスク管理部の承認を省略できます。",
            ]),
            ("remote", [
                "非対面で複雑な商品を販売する場合は、録画または録音を残し、管理者が説明内容を事前確認します。",
                "通信障害で記録が中断した場合は、その時点で申込みを確定せず、改めて説明を行います。",
                "顧客が書面説明を希望し、商品説明を伴う勧誘を行わない場合は、事前確認の対象外です。",
            ]),
            ("corporate", [
                "法人顧客のデリバティブ取引は、取締役会決議または権限規程で確認できる担当者から受注します。",
                "過去に同種取引の権限確認を行っていても、有効期限と担当者変更の有無を取引ごとに確認します。",
                "包括的な権限証明が有効期間内に登録されている場合は、決議書の再提出を省略できます。",
            ]),
        ],
    )


def build_record_context() -> list[dict[str, Any]]:
    return build_context_family(
        family="record-context",
        title="記録管理細則 2025年版",
        filename="record-management-2025.pdf",
        topics=[
            ("interview", [
                "顧客面談の記録は、契約終了後7年間保存することを原則とします。",
                "記録には説明した商品、リスク、顧客の質問、理解度確認、同席者、承認者を含めます。",
                "係争または調査が継続している場合は、7年を経過しても終了通知があるまで廃棄してはなりません。",
            ]),
            ("call", [
                "電話勧誘の録音は通話日から5年間保存します。",
                "録音と案件番号を結び付け、担当者以外の監査担当者が検索できる状態にします。",
                "顧客が録音に同意せず勧誘を中止した通話は、録音本体ではなく中止した事実と日時だけを保存します。",
            ]),
            ("access", [
                "顧客情報へのアクセスログは2年間オンラインで保持します。",
                "2年を経過したログは低頻度ストレージへ移し、合計7年間保存します。",
                "セキュリティ調査の対象となったログは、調査終了後1年間または通常期限の長い方まで保存します。",
            ]),
            ("draft", [
                "作成途中の契約書案は案件完了後90日で削除します。",
                "顧客へ提示した版と最終承認版は正式記録として7年間保存します。",
                "係争の証拠として指定された草案は90日を過ぎても削除対象から除外します。",
            ]),
            ("consent", [
                "個人情報利用の同意記録は、同意が有効な期間中と撤回後5年間保存します。",
                "同意の取得日時、対象目的、提示した規約版、取得経路を記録します。",
                "同意が無効と判明した場合でも、監査証跡として記録を直ちに削除せず、法務部の判断に従います。",
            ]),
        ],
    )


def build_suitability() -> list[dict[str, Any]]:
    rows = [
        ("01", "投資経験がほとんどなく元本の安全性を最優先する顧客には、複雑な仕組債を提案しません。預金や価格変動の小さい商品を含めて選択肢を説明します。"),
        ("02", "長期運用を希望し一時的な価格下落を許容できる顧客には、分散された株式商品を候補にできます。ただし生活資金を投資へ充てないことを確認します。"),
        ("03", "近く住宅購入を予定する顧客の資金は、換金制限のある商品に適しません。利用予定時期と換金期間を照合します。"),
        ("04", "為替変動を避けたい顧客へ外貨建て商品を案内する場合、為替ヘッジの有無と費用を比較し、希望と合わなければ提案を見送ります。"),
        ("05", "毎月の分配金を希望する顧客には、分配金が元本の払戻しとなる場合を説明します。分配額だけで適合性を判断しません。"),
        ("06", "短期的な利益を求める顧客でも、損失許容額が小さい場合にレバレッジ商品を提案することは適切ではありません。"),
        ("07", "法人顧客が余剰資金を運用する場合、資金使途、必要時期、社内権限、会計上の制約を確認して商品を選びます。"),
        ("08", "高い収益を希望していても、商品構造を理解できない顧客には複雑商品を販売しません。希望収益だけを根拠に適合性を認めないことが重要です。"),
        ("09", "複数商品を保有する顧客では、新規商品の単体リスクだけでなく、資産全体の通貨、地域、発行体の偏りを確認します。"),
        ("10", "相続した有価証券を保有する顧客へ売買を提案するときは、取得経緯と保有目的を確認します。過去の保有期間だけで投資経験を推定しません。"),
        ("11", "定期収入が減少した顧客については、以前と同じ投資意向が登録されていても、現在の余裕資金を再確認します。"),
        ("12", "元本保証を希望する顧客へ債券商品を提案する場合も、発行体の信用リスクと中途売却時の価格変動を説明します。"),
        ("13", "環境分野への投資を希望する顧客には、名称だけでなく投資対象と選定基準を説明し、期待するテーマと一致するか確認します。"),
        ("14", "取引頻度が高い顧客でも、手数料負担が収益機会を上回る状態では追加の乗換えを勧めません。"),
        ("15", "顧客が家族のために運用する場合は、名義人本人の目的とリスク許容度を確認します。家族の意向だけで商品を決定しません。"),
    ]
    return [
        document(
            id=f"suitability-{slug}",
            family="suitability",
            title="適合性確認ガイド 2025年版",
            filename="suitability-guide-2025.pdf",
            category="ガイド",
            body=body,
            identifiers=[f"SUIT-{slug}"],
            document_type="guide",
        )
        for slug, body in rows
    ]


def build_complaints() -> list[dict[str, Any]]:
    topics = [
        "商品リスクの説明不足", "手数料表示", "電話勧誘の継続", "解約処理の遅延", "システム停止",
        "本人確認", "相続手続", "価格配信", "広告表現", "担当者交代",
        "書面未着", "注文取消し", "分配金説明", "為替手数料", "個人情報",
    ]
    records = []
    for index, topic in enumerate(topics, start=1):
        body = (
            f"{topic}に関する申出を受け付けた担当者は、事実関係と顧客の希望を記録し、"
            "翌営業日までに顧客対応管理部へ引き継ぎます。回答期限を確約できない場合も、次回連絡日を案内します。"
        )
        records.append(
            document(
                id=f"complaint-{index:02d}",
                family="complaints",
                title="苦情対応手順 2025年版",
                filename="complaint-handbook-2025.pdf",
                category="手順",
                body=body,
                identifiers=[f"COMPLAINT-{index:02d}"],
                document_type="procedure",
            )
        )
    return records


def build_operations() -> list[dict[str, Any]]:
    rows = [
        ("E1047", "注文登録時に口座状態が更新中であることを示すエラーです。5分後に再実行し、解消しない場合は口座管理担当へ連絡します。注文を重複登録してはいけません。"),
        ("E1074", "注文金額が利用可能残高を超えていることを示すエラーです。残高と未約定注文を確認し、顧客の同意なく金額を変更しないでください。"),
        ("E1407", "商品コードが取扱対象外であることを示すエラーです。似た商品コードへ置き換えず、商品マスタの適用日を確認します。"),
        ("E1704", "承認者が申請者と同一であることを示すエラーです。別の承認者へ依頼し、申請を作り直す必要はありません。"),
        ("E2041", "顧客情報の必須項目が不足していることを示します。不足項目を確認し、推測値を入力せず顧客へ確認します。"),
        ("E2104", "本人確認書類の有効期限切れを示します。新しい書類の確認が完了するまで対象取引を受け付けません。"),
        ("E4017", "検索APIの認証情報が失効していることを示します。再ログインではなく、サービスアカウントの鍵更新状況を確認します。"),
        ("E4071", "検索対象テナントへの権限がないことを示します。クエリ条件からテナントfilterを外して回避してはいけません。"),
        ("E4107", "指定した文書が保存期限により移管済みであることを示します。アーカイブ検索を利用し、同じ文書を再登録しないでください。"),
        ("E4701", "一括出力件数が上限を超えています。対象期間を分割し、出力ごとに承認番号を記録します。"),
        ("JOB-017", "夜間の顧客属性更新ジョブです。処理中は口座状態が一時的に更新中となるため、注文登録を再試行する場合があります。"),
        ("JOB-071", "検索indexへ公開文書を反映するジョブです。失敗時は前回成功版を維持し、空のindexへ切り替えません。"),
        ("API-SEARCH-V2", "文書検索APIの第2版です。テナントと公開範囲のfilterは認証済みコンテキストから強制し、利用者入力では変更できません。"),
        ("API-INGEST-V2", "文書投入APIの第2版です。登録前に文書ID、版番号、公開日を検証し、同一版の重複投入を拒否します。"),
        ("BATCH-DELETE-01", "期限切れ一時データを削除する処理です。正式記録と法務保全対象は削除候補から除外し、件数を監査ログへ残します。"),
    ]
    return [
        document(
            id=f"operation-{code.lower()}",
            family="operations",
            title="システム運用手順 2025年版",
            filename="system-operation-2025.pdf",
            category="システム",
            body=body,
            identifiers=[code],
            document_type="procedure",
        )
        for code, body in rows
    ]


def build_market_cases() -> list[dict[str, Any]]:
    subjects = [
        ("01", "公表前情報を知った担当者が株式を購入したため、内部者取引の疑いとして調査対象になりました。"),
        ("02", "公表済みの決算情報だけを用いて顧客が株式を購入しており、内部者情報の利用は確認されませんでした。"),
        ("03", "注文を誘引する目的で約定意思のない大量注文を発注し、相場操縦に当たると判断されました。"),
        ("04", "大口注文を複数回に分けましたが、市場への影響を抑える執行計画に基づき、見せ玉ではありませんでした。"),
        ("05", "顧客注文の執行前に自己勘定で同じ銘柄を購入し、フロントランニングとして問題になりました。"),
        ("06", "顧客注文と自己勘定注文の時間が近接していましたが、独立した自動運用戦略によるものと確認されました。"),
        ("07", "終値を引き上げる目的で取引終了直前に反復注文を行い、不公正な価格形成と判断されました。"),
        ("08", "指数連動商品のリバランスに伴う終値付近の注文であり、事前計画と注文根拠が記録されていました。"),
        ("09", "虚偽の業績情報をSNSへ投稿して価格上昇後に売却し、風説の流布として調査されました。"),
        ("10", "企業が公式発表を訂正し、その内容を報道機関が転載したもので、投稿者による虚偽情報の作成ではありません。"),
        ("11", "複数口座を使って売買を繰り返し、取引が活発に見える外観を作った疑いが確認されました。"),
        ("12", "家族口座間の売買がありましたが、独立した投資判断と市場価格に基づく取引である記録が残っていました。"),
        ("13", "未公表の増資情報を取引先へ伝え、伝達を受けた者が売却したため情報伝達行為が問題となりました。"),
        ("14", "秘密保持契約下で情報を受領しましたが、情報隔壁により運用担当者には共有されず取引も停止されていました。"),
        ("15", "顧客の取消注文を意図的に処理せず自己勘定取引を優先したため、執行管理上の重大な違反となりました。"),
    ]
    return [
        document(
            id=f"market-case-{slug}",
            family="market-cases",
            title="取引審査事例集 2024年度",
            filename="market-review-cases-2024.pdf",
            category="事例",
            body=body,
            identifiers=[f"MARKET-{slug}"],
            document_type="case",
            case_outcome="violation" if int(slug) % 2 else "non_violation",
        )
        for slug, body in subjects
    ]


def query(
    id: str,
    split: str,
    category: str,
    text: str,
    relevance: dict[str, int],
    *,
    case_group: str,
    mode: str | None = None,
    filters: dict[str, Any] | None = None,
    required_context_ids: list[str] | None = None,
    expected_ids: list[str] | None = None,
    forbidden_ids: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": id,
        "split": split,
        "category": category,
        "case_group": case_group,
        "query": text,
        "relevance": relevance,
        "mode": mode,
        "filters": filters or {},
        "required_context_ids": required_context_ids or [],
        "expected_ids": expected_ids or [],
        "forbidden_ids": forbidden_ids or [],
    }


def build_queries() -> list[dict[str, Any]]:
    queries: list[dict[str, Any]] = []
    semantic = [
        ("dev", "sem-d01", "家族に同席してもらわず、危険性の説明も足りないまま高齢者へ複雑な商品を売ったケース", "elderly-case-01"),
        ("dev", "sem-d02", "顧客の運用損を取引先との関係維持費という名目で穴埋めしたケース", "comp-case-01"),
        ("dev", "sem-d03", "見ることはできるが、承認状態を触れない一般担当者の権限", "permission-view-01"),
        ("dev", "sem-d04", "金融商品の知識が乏しく安全性を優先する人に複雑な商品を勧めない考え方", "suitability-01"),
        ("dev", "sem-d05", "顧客注文より先に自社の売買を済ませた問題", "market-case-05"),
        ("test", "sem-t01", "説明した証拠が残っておらず、後から適切だったか確かめられない高齢者販売", "elderly-case-03"),
        ("test", "sem-t02", "全員向けに公開された施策なので、個別損失の埋め合わせではない還元", "comp-case-12"),
        ("test", "sem-t03", "住宅購入に使う予定の資金を、すぐ現金化できない商品へ入れるべきでない理由", "suitability-03"),
        ("test", "sem-t04", "取引が盛んなように見せるため、複数口座で売買を往復させたケース", "market-case-11"),
        ("test", "sem-t05", "顧客から断られた商品を短期間にもう一度案内してはいけない規定", "rule-020"),
    ]
    for split, qid, text, target in semantic:
        queries.append(query(qid, split, "semantic", text, {target: 3}, case_group=qid))

    lexical = [
        ("dev", "lex-d01", "第19条", "rule-019"),
        ("dev", "lex-d02", "ALPHA-01", "product-alpha-01"),
        ("dev", "lex-d03", "E1047", "operation-e1047"),
        ("dev", "lex-d04", "ADMIN-01", "permission-admin-01"),
        ("dev", "lex-d05", "第19条の2", "rule-019-2"),
        ("test", "lex-t01", "ALPHA-10", "product-alpha-10"),
        ("test", "lex-t02", "E1407", "operation-e1407"),
        ("test", "lex-t03", "RULE-020", "rule-020"),
        ("test", "lex-t04", "API-SEARCH-V2", "operation-api-search-v2"),
        ("test", "lex-t05", "OMEGA-50", "product-omega-50"),
    ]
    for split, qid, text, target in lexical:
        queries.append(query(qid, split, "lexical", text, {target: 3}, case_group=qid))

    mixed = [
        ("dev", "mix-d01", "ALPHA-07で為替の値動きを抑える仕組み", "product-alpha-07"),
        ("dev", "mix-d02", "E1074が出たとき注文額を勝手に変えてよいか", "operation-e1074"),
        ("dev", "mix-d03", "第25条の面談記録はいつまで残すか", "rule-025"),
        ("dev", "mix-d04", "DELTA-30を長期保有すると指数の逆方向とずれる理由", "product-delta-30"),
        ("dev", "mix-d05", "EXPORT-01で通常管理者だけでは一括出力できない理由", "permission-export-01"),
        ("test", "mix-t01", "ALPHA-10を現金化するまでの日数と主な価格変動要因", "product-alpha-10"),
        ("test", "mix-t02", "E4071をテナント条件を外して回避してはいけない理由", "operation-e4071"),
        ("test", "mix-t03", "第29条で新しい手数料を知らせる期限", "rule-029"),
        ("test", "mix-t04", "OMEGA-05で参照指数が下がった場合の元本への影響", "product-omega-05"),
        ("test", "mix-t05", "APPROVE-01でリスク管理部の追加承認が必要になる金額", "permission-approve-01"),
    ]
    for split, qid, text, target in mixed:
        queries.append(query(qid, split, "mixed", text, {target: 3}, case_group=qid))

    negation = [
        ("dev", "neg-d01", "高リスク商品の勧誘を行わなかった高齢顧客の事例", "elderly-case-02"),
        ("dev", "neg-d02", "過徴収の返金であり損失補てんには当たらなかった事例", "comp-case-02"),
        ("dev", "neg-d03", "一般担当者が変更できない監査記録の項目", "permission-view-01"),
        ("dev", "neg-d04", "顧客注文に先回りした取引ではなかった事例", "market-case-06"),
        ("dev", "neg-d05", "元本保証を望む顧客にも債券の価格変動を説明する必要があるか", "suitability-12"),
        ("test", "neg-t01", "投資商品の案内をせず普通預金へ入金した高齢顧客対応", "elderly-case-14"),
        ("test", "neg-t02", "投資損失ではなく事務事故の実費を賠償した事例", "comp-case-08"),
        ("test", "neg-t03", "外部委託先が参照できない情報", "permission-read-02"),
        ("test", "neg-t04", "終値付近の注文だが相場操縦ではなかった事例", "market-case-08"),
        ("test", "neg-t05", "高収益を希望しても商品を理解できなければ販売しない判断", "suitability-08"),
    ]
    for split, qid, text, target in negation:
        queries.append(query(qid, split, "negation_exception", text, {target: 3}, case_group=qid))

    contexts = [
        ("dev", "ctx-d01", "高齢顧客の継続購入で使える簡易承認の前提と例外", "approval-context-elderly"),
        ("dev", "ctx-d02", "夜間に口座を暫定停止した後、いつまでに何をするか", "approval-context-urgent"),
        ("dev", "ctx-d03", "面談記録の保存期間と、調査中に廃棄できない条件", "record-context-interview"),
        ("test", "ctx-t01", "高額取引を分割した場合の判定と承認を省略できる例外", "approval-context-high-value"),
        ("test", "ctx-t02", "顧客が録音を断って勧誘を中止した通話で残す情報", "record-context-call"),
        ("test", "ctx-t03", "作成途中の契約書案を90日後も削除してはいけない条件", "record-context-draft"),
    ]
    for split, qid, text, parent in contexts:
        ids = [f"{parent}-{index}" for index in range(1, 4)]
        queries.append(
            query(
                qid,
                split,
                "context",
                text,
                {chunk_id: 3 if chunk_id.endswith("-3") else 1 for chunk_id in ids},
                case_group=parent,
                mode="hybrid_context",
                required_context_ids=ids,
            )
        )

    queries.extend([
        query(
            "strict-d01", "dev", "constraint", "ALPHA-01", {"product-alpha-01": 3},
            case_group="strict-alpha-01", mode="exact",
            expected_ids=["product-alpha-01"], forbidden_ids=["product-alpha-10"],
        ),
        query(
            "strict-d02", "dev", "constraint", "複雑な仕組債を販売した事例", {"elderly-case-01": 3},
            case_group="strict-elderly-01", mode="hybrid_filter",
            filters={"document_type": "case", "customer_age_gte": 75, "amount_yen_gte": 5_000_000, "case_outcome": "violation"},
            expected_ids=["elderly-case-01"], forbidden_ids=["elderly-case-02", "elderly-case-04"],
        ),
        query(
            "strict-t01", "test", "constraint", "E1407", {"operation-e1407": 3},
            case_group="strict-e1407", mode="exact",
            expected_ids=["operation-e1407"], forbidden_ids=["operation-e1047", "operation-e1704"],
        ),
        query(
            "strict-t02", "test", "constraint", "高齢顧客へ販売した記録", {"elderly-case-03": 3, "elderly-case-06": 2},
            case_group="strict-elderly-03", mode="hybrid_filter",
            filters={"document_type": "case", "customer_age_gte": 80, "amount_yen_gte": 2_000_000},
            expected_ids=["elderly-case-03"], forbidden_ids=["elderly-case-01", "elderly-case-09"],
        ),
    ])
    return queries


def main() -> None:
    documents = (
        build_rules()
        + build_products()
        + build_deadlines()
        + build_elderly_cases()
        + build_compensation_cases()
        + build_permissions()
        + build_approval_context()
        + build_record_context()
        + build_suitability()
        + build_complaints()
        + build_operations()
        + build_market_cases()
    )
    queries = build_queries()
    if len(documents) != 180:
        raise RuntimeError(f"expected 180 documents, got {len(documents)}")
    if len(queries) != 50:
        raise RuntimeError(f"expected 50 queries, got {len(queries)}")

    CORPUS_PATH.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in documents),
        encoding="utf-8",
    )
    QUERIES_PATH.write_text(
        json.dumps(queries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(documents)} documents and {len(queries)} queries")


if __name__ == "__main__":
    main()
