import boto3
from datetime import datetime
from typing import Optional, Dict, Any
import json


class SendLineService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
        self.table_name = 'line_transaction_t'
        self.table = self.dynamodb.Table(self.table_name)

    def _get_current_timestamp(self) -> str:
        """現在のタイムスタンプを取得"""
        return datetime.now().isoformat()

    def write_line_transaction(
        self,
        lmn: str,
        transaction_type: Optional[str] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        amount: Optional[float] = None,
        line_user_id: Optional[str] = None,
        line_message: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        line_transaction_tテーブルにレコードを書き込み
        Args:
            lmn: プライマリキー（Line Message Number）
            transaction_type: 取引の種類（収入/支出）
            category: カテゴリ
            description: 説明・メモ
            amount: 金額
            line_user_id: LINEユーザーID
            line_message: LINEメッセージ内容
            additional_data: 追加データ（辞書形式）

        Returns:
            Dict[str, Any]: 書き込み結果
        """
        current_time = self._get_current_timestamp()

        # 基本アイテムを作成
        item = {
            'lmn': lmn,  # プライマリキー
            'created_at': current_time,
            'updated_at': current_time,
            'deleted_at': None,
            'transaction_type': transaction_type,
            'category': category,
            'description': description,
            'amount': amount,
            'line_user_id': line_user_id,
            'line_message': line_message
        }

        # 追加データがある場合はマージ
        if additional_data:
            item.update(additional_data)

        # None値を除外
        item = {k: v for k, v in item.items() if v is not None}

        try:
            response = self.table.put_item(Item=item)
            return {
                'success': True,
                'data': item,
                'response': response,
                'message': 'Line transaction written successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to write line transaction'
            }

    def write_from_line_message(
        self,
        line_user_id: str,
        line_message: str,
        parsed_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        LINEメッセージから解析したデータを書き込み

        Args:
            line_user_id: LINEユーザーID
            line_message: 元のLINEメッセージ
            parsed_data: 解析済みデータ（transaction_type, category, amount等）

        Returns:
            Dict[str, Any]: 書き込み結果
        """
        # lmnを生成（タイムスタンプベース）
        current_time = datetime.now()
        lmn = f"lmn_{line_user_id}_{current_time.strftime('%Y%m%d_%H%M%S_%f')}"

        # 解析データをマージ
        write_data = {
            'line_user_id': line_user_id,
            'line_message': line_message
        }

        if parsed_data:
            write_data.update(parsed_data)

        return self.write_line_transaction(
            lmn=lmn,
            **write_data
        )

    def update_line_transaction(
        self,
        lmn: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        line_transaction_tテーブルのレコードを更新

        Args:
            lmn: プライマリキー
            **kwargs: 更新するフィールド

        Returns:
            Dict[str, Any]: 更新結果
        """
        try:
            # 更新するフィールドを準備
            update_expression = "SET updated_at = :updated_at"
            expression_attribute_values = {
                ':updated_at': self._get_current_timestamp()
            }

            # 更新するフィールドを追加
            for key, value in kwargs.items():
                if key != 'lmn' and value is not None:  # lmnは更新しない
                    update_expression += f", {key} = :{key}"
                    expression_attribute_values[f':{key}'] = value

            response = self.table.update_item(
                Key={'lmn': lmn},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW"
            )

            return {
                'success': True,
                'data': response.get('Attributes', {}),
                'response': response,
                'message': 'Line transaction updated successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to update line transaction'
            }

    def read_line_transaction(self, lmn: str) -> Dict[str, Any]:
        """
        line_transaction_tテーブルからレコードを読み取り

        Args:
            lmn: プライマリキー

        Returns:
            Dict[str, Any]: 読み取り結果
        """
        try:
            response = self.table.get_item(Key={'lmn': lmn})

            if 'Item' in response:
                return {
                    'success': True,
                    'data': response['Item'],
                    'message': 'Line transaction found'
                }
            else:
                return {
                    'success': False,
                    'error': 'Item not found',
                    'message': f'Line transaction with lmn {lmn} not found'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to read line transaction'
            }

    def do(self):
        """既存のdoメソッド（必要に応じて実装）"""
        pass
