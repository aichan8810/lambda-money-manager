"""
SendLineServiceの使用例
"""

from Services.SendLineService import SendLineService


def line_service_example():
    """SendLineServiceの使用例"""

    # SendLineServiceのインスタンスを作成
    line_service = SendLineService()

    # 1. 基本的な書き込み
    print("=== 1. 基本的な書き込み ===")
    result1 = line_service.write_line_transaction(
        lmn="lmn_user123_20241201_001",
        transaction_type="支出",
        category="食費",
        description="昼食代",
        amount=850.0,
        line_user_id="U1234567890abcdef",
        line_message="昼食 850円"
    )
    print(f"書き込み結果1: {result1}")

    # 2. LINEメッセージから自動生成
    print("\n=== 2. LINEメッセージから自動生成 ===")
    parsed_data = {
        "transaction_type": "支出",
        "category": "交通費",
        "description": "電車代",
        "amount": 200.0
    }

    result2 = line_service.write_from_line_message(
        line_user_id="U1234567890abcdef",
        line_message="電車代 200円",
        parsed_data=parsed_data
    )
    print(f"書き込み結果2: {result2}")

    # 3. 追加データ付きで書き込み
    print("\n=== 3. 追加データ付きで書き込み ===")
    additional_data = {
        "location": "新宿駅",
        "payment_method": "ICカード",
        "receipt_number": "R123456789"
    }

    result3 = line_service.write_line_transaction(
        lmn="lmn_user123_20241201_003",
        transaction_type="支出",
        category="交通費",
        description="電車代",
        amount=200.0,
        line_user_id="U1234567890abcdef",
        line_message="電車代 200円",
        additional_data=additional_data
    )
    print(f"書き込み結果3: {result3}")

    # 4. レコードを読み取り
    print("\n=== 4. レコード読み取り ===")
    read_result = line_service.read_line_transaction("lmn_user123_20241201_001")
    print(f"読み取り結果: {read_result}")

    # 5. レコードを更新
    print("\n=== 5. レコード更新 ===")
    update_result = line_service.update_line_transaction(
        "lmn_user123_20241201_001",
        description="昼食代（コンビニ弁当）",
        amount=900.0,
        line_message="昼食 900円（コンビニ弁当）"
    )
    print(f"更新結果: {update_result}")

    # 6. 複数のLINEメッセージを一括処理
    print("\n=== 6. 複数のLINEメッセージを一括処理 ===")
    line_messages = [
        {
            "user_id": "U1234567890abcdef",
            "message": "給与 300000円",
            "parsed_data": {
                "transaction_type": "収入",
                "category": "給与",
                "description": "12月給与",
                "amount": 300000.0
            }
        },
        {
            "user_id": "U1234567890abcdef",
            "message": "家賃 80000円",
            "parsed_data": {
                "transaction_type": "支出",
                "category": "住居費",
                "description": "12月家賃",
                "amount": 80000.0
            }
        },
        {
            "user_id": "U1234567890abcdef",
            "message": "光熱費 15000円",
            "parsed_data": {
                "transaction_type": "支出",
                "category": "光熱費",
                "description": "12月光熱費",
                "amount": 15000.0
            }
        }
    ]

    for i, msg_data in enumerate(line_messages, 1):
        result = line_service.write_from_line_message(
            line_user_id=msg_data["user_id"],
            line_message=msg_data["message"],
            parsed_data=msg_data["parsed_data"]
        )
        print(f"メッセージ{i}書き込み結果: {result['success']}")


if __name__ == "__main__":
    line_service_example()
