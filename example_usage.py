"""
DynamoDB汎用CRUDクラスの使用例
"""

from Models.Money import Money


def example_usage():
    """使用例"""

    # 1. 新しいお金レコードを作成
    print("=== 1. レコード作成 ===")
    money_record = Money.create_money_record(
        pk="user123_20241201_001",
        transaction_type="支出",
        category="食費",
        description="昼食代",
        amount=850.0
    )

    # レコードをDynamoDBに保存
    create_result = money_record.create()
    print(f"作成結果: {create_result}")

    # 2. レコードを読み取り
    print("\n=== 2. レコード読み取り ===")
    read_result = money_record.read("user123_20241201_001")
    print(f"読み取り結果: {read_result}")

    # 3. レコードを更新
    print("\n=== 3. レコード更新 ===")
    update_result = money_record.update(
        "user123_20241201_001",
        description="昼食代（コンビニ弁当）",
        amount=900.0
    )
    print(f"更新結果: {update_result}")

    # 4. 収入レコードを作成
    print("\n=== 4. 収入レコード作成 ===")
    income_record = Money.create_money_record(
        pk="user123_20241201_002",
        transaction_type="収入",
        category="給与",
        description="12月給与",
        amount=300000.0
    )
    income_create_result = income_record.create()
    print(f"収入レコード作成結果: {income_create_result}")

    # 5. 支出レコードを取得
    print("\n=== 5. 支出レコード取得 ===")
    expense_records = money_record.get_expense_records()
    print(f"支出レコード: {expense_records}")

    # 6. 収入レコードを取得
    print("\n=== 6. 収入レコード取得 ===")
    income_records = money_record.get_income_records()
    print(f"収入レコード: {income_records}")

    # 7. 合計金額を計算
    print("\n=== 7. 合計金額計算 ===")
    total_income = money_record.get_total_amount("収入")
    total_expense = money_record.get_total_amount("支出")
    total_all = money_record.get_total_amount()

    print(f"収入合計: {total_income}")
    print(f"支出合計: {total_expense}")
    print(f"全体合計: {total_all}")

    # 8. 月次サマリーを取得
    print("\n=== 8. 月次サマリー ===")
    monthly_summary = money_record.get_monthly_summary(2024, 12)
    print(f"12月サマリー: {monthly_summary}")

    # 9. 全レコードを取得
    print("\n=== 9. 全レコード取得 ===")
    all_records = money_record.list_all()
    print(f"全レコード: {all_records}")

    # 10. 論理削除
    print("\n=== 10. 論理削除 ===")
    delete_result = money_record.delete("user123_20241201_001", soft_delete=True)
    print(f"削除結果: {delete_result}")

    # 11. 削除済みを除く全レコードを取得
    print("\n=== 11. 削除済みを除く全レコード ===")
    active_records = money_record.list_all(include_deleted=False)
    print(f"アクティブなレコード: {active_records}")


if __name__ == "__main__":
    example_usage()
