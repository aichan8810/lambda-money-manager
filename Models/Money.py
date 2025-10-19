from .DynamoDBModel import DynamoDBModel
from typing import Optional


class Money(DynamoDBModel):
    """
    お金の管理用モデルクラス
    DynamoDBModelを継承してCRUD操作を提供
    """

    class Config:
        table_name = "money_table"  # テーブル名を指定
        region_name = "ap-northeast-1"

    def __init__(self, pk: str, **kwargs):
        super().__init__(pk=pk, **kwargs)

    @classmethod
    def create_money_record(
        cls,
        pk: str,
        transaction_type: Optional[str] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        amount: Optional[float] = None
    ) -> 'Money':
        """
        新しいお金レコードを作成するファクトリメソッド

        Args:
            pk: プライマリキー
            transaction_type: 取引の種類（例：収入、支出）
            category: カテゴリ（例：食費、交通費、給与）
            description: 説明・メモ
            amount: 金額

        Returns:
            Money: 作成されたMoneyインスタンス
        """
        return cls(
            pk=pk,
            transaction_type=transaction_type,
            category=category,
            description=description,
            amount=amount
        )

    def get_income_records(self) -> dict:
        """収入レコードを取得"""
        return self.query_by_transaction_type("収入")

    def get_expense_records(self) -> dict:
        """支出レコードを取得"""
        return self.query_by_transaction_type("支出")

    def get_records_by_category(self, category: str) -> dict:
        """指定したカテゴリのレコードを取得"""
        return self.query_by_category(category)

    def get_total_amount(self, transaction_type: Optional[str] = None) -> dict:
        """
        合計金額を計算

        Args:
            transaction_type: 指定した場合、その種類のみの合計を計算

        Returns:
            dict: 合計金額とレコード数
        """
        if transaction_type:
            result = self.query_by_transaction_type(transaction_type)
        else:
            result = self.list_all()

        if not result['success']:
            return result

        total_amount = 0
        for item in result['data']:
            if item.get('amount') is not None:
                total_amount += float(item['amount'])

        return {
            'success': True,
            'total_amount': total_amount,
            'record_count': len(result['data']),
            'transaction_type': transaction_type
        }

    def get_monthly_summary(self, year: int, month: int) -> dict:
        """
        月次サマリーを取得

        Args:
            year: 年
            month: 月

        Returns:
            dict: 月次サマリー情報
        """
        # 月の開始日と終了日を計算
        from datetime import datetime, date
        start_date = datetime(year, month, 1).isoformat()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).isoformat()
        else:
            end_date = datetime(year, month + 1, 1).isoformat()

        try:
            # 月の範囲でフィルタリング
            response = self.table.scan(
                FilterExpression="created_at BETWEEN :start_date AND :end_date AND attribute_not_exists(deleted_at)",
                ExpressionAttributeValues={
                    ':start_date': start_date,
                    ':end_date': end_date
                }
            )

            records = response.get('Items', [])

            # 収入と支出を分けて集計
            income_total = 0
            expense_total = 0
            income_count = 0
            expense_count = 0

            for record in records:
                amount = record.get('amount', 0) or 0
                transaction_type = record.get('transaction_type', '')

                if transaction_type == '収入':
                    income_total += amount
                    income_count += 1
                elif transaction_type == '支出':
                    expense_total += amount
                    expense_count += 1

            return {
                'success': True,
                'year': year,
                'month': month,
                'income_total': income_total,
                'expense_total': expense_total,
                'net_amount': income_total - expense_total,
                'income_count': income_count,
                'expense_count': expense_count,
                'total_records': len(records)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
