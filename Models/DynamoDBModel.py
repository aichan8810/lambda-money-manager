import boto3
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import json


class DynamoDBModel(BaseModel):
    """
    DynamoDBの汎用CRUD操作を提供するベースクラス
    """
    pk: str = Field(..., description="プライマリキー")
    created_at: Optional[str] = Field(default=None, description="作成日時")
    updated_at: Optional[str] = Field(default=None, description="更新日時")
    deleted_at: Optional[str] = Field(default=None, description="削除日時")
    transaction_type: Optional[str] = Field(default=None, description="取引の種類（収入/支出）")
    category: Optional[str] = Field(default=None, description="カテゴリ")
    description: Optional[str] = Field(default=None, description="説明・メモ")
    amount: Optional[float] = Field(default=None, description="金額")

    class Config:
        table_name: str = ""
        region_name: str = "ap-northeast-1"

    def __init__(self, **data):
        super().__init__(**data)
        self.dynamodb = boto3.resource('dynamodb', region_name=self.Config.region_name)
        self.table = self.dynamodb.Table(self.Config.table_name)

    def _get_current_timestamp(self) -> str:
        """現在のタイムスタンプを取得"""
        return datetime.now().isoformat()

    def create(self) -> Dict[str, Any]:
        """レコードを作成"""
        current_time = self._get_current_timestamp()

        item = {
            'pk': self.pk,
            'created_at': current_time,
            'updated_at': current_time,
            'deleted_at': None,
            'transaction_type': self.transaction_type,
            'category': self.category,
            'description': self.description,
            'amount': self.amount
        }

        # None値を除外
        item = {k: v for k, v in item.items() if v is not None}

        try:
            response = self.table.put_item(Item=item)
            return {
                'success': True,
                'data': item,
                'response': response
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def read(self, pk: str) -> Dict[str, Any]:
        """レコードを読み取り"""
        try:
            response = self.table.get_item(Key={'pk': pk})

            if 'Item' in response:
                return {
                    'success': True,
                    'data': response['Item']
                }
            else:
                return {
                    'success': False,
                    'error': 'Item not found'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def update(self, pk: str, **kwargs) -> Dict[str, Any]:
        """レコードを更新"""
        try:
            # 更新するフィールドを準備
            update_expression = "SET updated_at = :updated_at"
            expression_attribute_values = {
                ':updated_at': self._get_current_timestamp()
            }

            # 更新するフィールドを追加
            for key, value in kwargs.items():
                if key != 'pk' and value is not None:  # pkは更新しない
                    update_expression += f", {key} = :{key}"
                    expression_attribute_values[f':{key}'] = value

            response = self.table.update_item(
                Key={'pk': pk},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW"
            )

            return {
                'success': True,
                'data': response.get('Attributes', {}),
                'response': response
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def delete(self, pk: str, soft_delete: bool = True) -> Dict[str, Any]:
        """レコードを削除（論理削除または物理削除）"""
        try:
            if soft_delete:
                # 論理削除
                response = self.table.update_item(
                    Key={'pk': pk},
                    UpdateExpression="SET deleted_at = :deleted_at",
                    ExpressionAttributeValues={
                        ':deleted_at': self._get_current_timestamp()
                    },
                    ReturnValues="ALL_NEW"
                )
                return {
                    'success': True,
                    'data': response.get('Attributes', {}),
                    'response': response
                }
            else:
                # 物理削除
                response = self.table.delete_item(Key={'pk': pk})
                return {
                    'success': True,
                    'data': {'pk': pk},
                    'response': response
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def list_all(self, include_deleted: bool = False) -> Dict[str, Any]:
        """全レコードを取得"""
        try:
            if include_deleted:
                # 削除済みも含めて全件取得
                response = self.table.scan()
            else:
                # 削除済みを除外して取得
                response = self.table.scan(
                    FilterExpression="attribute_not_exists(deleted_at)"
                )

            return {
                'success': True,
                'data': response.get('Items', []),
                'count': response.get('Count', 0)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def query_by_transaction_type(self, transaction_type: str) -> Dict[str, Any]:
        """transaction_typeでクエリ"""
        try:
            response = self.table.scan(
                FilterExpression="transaction_type = :transaction_type AND attribute_not_exists(deleted_at)",
                ExpressionAttributeValues={
                    ':transaction_type': transaction_type
                }
            )

            return {
                'success': True,
                'data': response.get('Items', []),
                'count': response.get('Count', 0)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def query_by_category(self, category: str) -> Dict[str, Any]:
        """categoryでクエリ"""
        try:
            response = self.table.scan(
                FilterExpression="category = :category AND attribute_not_exists(deleted_at)",
                ExpressionAttributeValues={
                    ':category': category
                }
            )

            return {
                'success': True,
                'data': response.get('Items', []),
                'count': response.get('Count', 0)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def to_json(self) -> Dict[str, Any]:
        """JSON形式でデータを返す"""
        return self.dict()
