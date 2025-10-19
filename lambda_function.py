import json
import logging
from Controllers.IndexController import IndexController
from Services.SendLineService import SendLineService
from Models.LineRequest import LineRequest

# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handleLineForMoney(event, context):
    """
    LINEからのメッセージを処理してDynamoDBに保存するLambda関数

    Args:
        event: Lambda イベント（LINE Webhookからのデータ）
        context: Lambda コンテキスト

    Returns:
        dict: HTTPレスポンス
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        # リクエストボディを取得
        if 'body' in event:
            body = event['body']
            if isinstance(body, str):
                body = json.loads(body)
        else:
            body = event

        # LINE Webhookの検証
        if not _is_valid_line_webhook(body):
            logger.warning("Invalid LINE webhook data")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid LINE webhook data'})
            }

        # LINEメッセージを処理
        result = _process_line_messages(body)

        if result['success']:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Messages processed successfully',
                    'processed_count': result['processed_count']
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Failed to process messages',
                    'details': result['error']
                })
            }

    except Exception as e:
        logger.error(f"Error processing LINE message: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }


def _is_valid_line_webhook(body):
    """
    LINE Webhookのデータが有効かチェック

    Args:
        body: リクエストボディ

    Returns:
        bool: 有効な場合True
    """
    try:
        # LINE Webhookの基本的な構造をチェック
        if 'events' not in body:
            return False

        events = body['events']
        if not isinstance(events, list) or len(events) == 0:
            return False

        # 最初のイベントがメッセージイベントかチェック
        first_event = events[0]
        if first_event.get('type') != 'message':
            return False

        if 'message' not in first_event:
            return False

        return True

    except Exception as e:
        logger.error(f"Error validating LINE webhook: {str(e)}")
        return False


def _process_line_messages(body):
    """
    LINEメッセージを処理してDynamoDBに保存

    Args:
        body: LINE Webhookのリクエストボディ

    Returns:
        dict: 処理結果
    """
    try:
        line_service = SendLineService()
        processed_count = 0

        events = body.get('events', [])

        for event in events:
            if event.get('type') != 'message':
                continue

            message = event.get('message', {})
            if message.get('type') != 'text':
                continue

            # ユーザーIDとメッセージテキストを取得
            user_id = event.get('source', {}).get('userId')
            message_text = message.get('text', '')

            if not user_id or not message_text:
                continue

            # メッセージを解析（簡単なパターンマッチング）
            parsed_data = _parse_message(message_text)

            # DynamoDBに保存
            result = line_service.write_from_line_message(
                line_user_id=user_id,
                line_message=message_text,
                parsed_data=parsed_data
            )

            if result['success']:
                processed_count += 1
                logger.info(f"Successfully processed message from user {user_id}: {message_text}")
            else:
                logger.error(f"Failed to process message from user {user_id}: {result['error']}")

        return {
            'success': True,
            'processed_count': processed_count
        }

    except Exception as e:
        logger.error(f"Error processing LINE messages: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def _parse_message(message_text):
    """
    メッセージテキストを解析してデータを抽出

    Args:
        message_text: LINEメッセージのテキスト

    Returns:
        dict: 解析されたデータ
    """
    try:
        # 簡単なパターンマッチング例
        # 例: "昼食 850円" -> 支出, 食費, 850
        # 例: "給与 300000円" -> 収入, 給与, 300000

        import re

        # 金額を抽出
        amount_match = re.search(r'(\d+(?:,\d{3})*(?:\.\d+)?)', message_text)
        amount = None
        if amount_match:
            amount_str = amount_match.group(1).replace(',', '')
            amount = float(amount_str)

        # キーワードベースでカテゴリを判定
        category = "その他"
        transaction_type = "支出"  # デフォルトは支出

        # 収入のキーワード
        income_keywords = ['給与', 'ボーナス', '賞与', '収入', '入金', '売上']
        if any(keyword in message_text for keyword in income_keywords):
            transaction_type = "収入"
            if '給与' in message_text or 'ボーナス' in message_text or '賞与' in message_text:
                category = "給与"
            else:
                category = "収入"

        # 支出のカテゴリ
        else:
            if any(keyword in message_text for keyword in ['食費', '食事', '昼食', '夕食', '朝食', '弁当', 'レストラン']):
                category = "食費"
            elif any(keyword in message_text for keyword in ['交通費', '電車', 'バス', 'タクシー', 'ガソリン']):
                category = "交通費"
            elif any(keyword in message_text for keyword in ['家賃', '住居費', '賃貸']):
                category = "住居費"
            elif any(keyword in message_text for keyword in ['光熱費', '電気', 'ガス', '水道']):
                category = "光熱費"
            elif any(keyword in message_text for keyword in ['医療費', '病院', '薬']):
                category = "医療費"
            elif any(keyword in message_text for keyword in ['娯楽', '映画', 'ゲーム', '本']):
                category = "娯楽費"
            elif any(keyword in message_text for keyword in ['買い物', 'ショッピング', '服', '雑貨']):
                category = "買い物"

        return {
            'transaction_type': transaction_type,
            'category': category,
            'description': message_text,
            'amount': amount
        }

    except Exception as e:
        logger.error(f"Error parsing message: {str(e)}")
        return {
            'transaction_type': '支出',
            'category': 'その他',
            'description': message_text,
            'amount': None
        }


# テスト用のハンドラー
def lambda_handler(event, context):
    """
    AWS Lambdaのメインハンドラー
    """
    return handleLineForMoney(event, context)
