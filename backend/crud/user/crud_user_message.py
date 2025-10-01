from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime

class CRUDUserMessage:
    def __init__(self):
        pass

    async def create_private_message(
        self,
        db: Session,
        sender_id: int,
        receiver_id: int,
        content: str,
        message_type: str = "private"
    ) -> Any:
        """创建私信记录（标记消息类型为"导师私信"）"""
        try:
            query = """
            INSERT INTO private_messages 
            (sender_id, receiver_id, content, message_type, is_read, created_at)
            VALUES (:sender_id, :receiver_id, :content, :message_type, false, :created_at)
            RETURNING id, sender_id, receiver_id, content, message_type, is_read, created_at
            """
            
            result = db.execute(query, {
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "content": content,
                "message_type": message_type,
                "created_at": datetime.now()
            }).fetchone()
            
            db.commit()
            
            if result:
                return PrivateMessageData(
                    id=result.id,
                    sender_id=result.sender_id,
                    receiver_id=result.receiver_id,
                    content=result.content,
                    message_type=result.message_type,
                    is_read=result.is_read,
                    created_at=result.created_at
                )
            return None
        except Exception as e:
            db.rollback()
            raise Exception(f"创建私信失败: {str(e)}")

    async def get_messages_between_users(
        self,
        db: Session,
        user1_id: int,
        user2_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Any]:
        """获取两个用户之间的私信记录"""
        try:
            query = """
            SELECT 
                id, sender_id, receiver_id, content, message_type, 
                is_read, created_at, updated_at
            FROM private_messages 
            WHERE (sender_id = :user1_id AND receiver_id = :user2_id)
               OR (sender_id = :user2_id AND receiver_id = :user1_id)
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
            """
            
            results = db.execute(query, {
                "user1_id": user1_id,
                "user2_id": user2_id,
                "limit": limit,
                "offset": skip
            }).fetchall()
            
            messages = []
            for result in results:
                messages.append(PrivateMessageData(
                    id=result.id,
                    sender_id=result.sender_id,
                    receiver_id=result.receiver_id,
                    content=result.content,
                    message_type=result.message_type,
                    is_read=result.is_read,
                    created_at=result.created_at,
                    updated_at=getattr(result, 'updated_at', None)
                ))
            
            return messages
        except Exception as e:
            raise Exception(f"获取私信记录失败: {str(e)}")

    async def get_user_conversations(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[Any]:
        """获取用户的会话列表（最近联系人）"""
        try:
            query = """
            WITH latest_messages AS (
                SELECT 
                    CASE 
                        WHEN sender_id = :user_id THEN receiver_id 
                        ELSE sender_id 
                    END as other_user_id,
                    MAX(created_at) as last_message_time,
                    (SELECT content FROM private_messages pm2 
                     WHERE ((pm2.sender_id = :user_id AND pm2.receiver_id = other_user_id) 
                            OR (pm2.sender_id = other_user_id AND pm2.receiver_id = :user_id))
                     ORDER BY pm2.created_at DESC LIMIT 1) as last_content,
                    (SELECT COUNT(*) FROM private_messages pm3 
                     WHERE pm3.sender_id = other_user_id 
                     AND pm3.receiver_id = :user_id 
                     AND pm3.is_read = false) as unread_count
                FROM private_messages 
                WHERE sender_id = :user_id OR receiver_id = :user_id
                GROUP BY other_user_id
            )
            SELECT * FROM latest_messages 
            ORDER BY last_message_time DESC
            LIMIT :limit OFFSET :offset
            """
            
            results = db.execute(query, {
                "user_id": user_id,
                "limit": limit,
                "offset": skip
            }).fetchall()
            
            conversations = []
            for result in results:
                conversations.append({
                    "other_user_id": result.other_user_id,
                    "last_message_time": result.last_message_time,
                    "last_content": result.last_content,
                    "unread_count": result.unread_count
                })
            
            return conversations
        except Exception as e:
            raise Exception(f"获取会话列表失败: {str(e)}")

    async def mark_messages_as_read(
        self,
        db: Session,
        receiver_id: int,
        sender_id: int
    ) -> bool:
        """标记消息为已读"""
        try:
            query = """
            UPDATE private_messages 
            SET is_read = true, updated_at = :updated_at
            WHERE receiver_id = :receiver_id 
            AND sender_id = :sender_id 
            AND is_read = false
            """
            
            db.execute(query, {
                "receiver_id": receiver_id,
                "sender_id": sender_id,
                "updated_at": datetime.now()
            })
            db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            raise Exception(f"标记消息已读失败: {str(e)}")

    async def get_unread_count(self, db: Session, user_id: int) -> int:
        """获取用户未读消息总数"""
        try:
            query = """
            SELECT COUNT(*) as count
            FROM private_messages 
            WHERE receiver_id = :user_id AND is_read = false
            """
            
            result = db.execute(query, {"user_id": user_id}).fetchone()
            return result.count if result else 0
        except Exception as e:
            raise Exception(f"获取未读消息数失败: {str(e)}")

    async def delete_message(self, db: Session, message_id: int, user_id: int) -> bool:
        """删除消息（只能删除自己发送的消息）"""
        try:
            query = """
            DELETE FROM private_messages 
            WHERE id = :message_id AND sender_id = :user_id
            """
            
            result = db.execute(query, {
                "message_id": message_id,
                "user_id": user_id
            })
            db.commit()
            
            return result.rowcount > 0
        except Exception as e:
            db.rollback()
            raise Exception(f"删除消息失败: {str(e)}")

    async def get_message_stats(self, db: Session, user_id: int) -> Dict[str, Any]:
        """获取用户消息统计"""
        try:
            # 发送消息数
            sent_query = """
            SELECT COUNT(*) as count FROM private_messages WHERE sender_id = :user_id
            """
            sent_result = db.execute(sent_query, {"user_id": user_id}).fetchone()
            sent_count = sent_result.count if sent_result else 0
            
            # 接收消息数
            received_query = """
            SELECT COUNT(*) as count FROM private_messages WHERE receiver_id = :user_id
            """
            received_result = db.execute(received_query, {"user_id": user_id}).fetchone()
            received_count = received_result.count if received_result else 0
            
            # 未读消息数
            unread_count = await self.get_unread_count(db, user_id)
            
            # 会话数
            conversations_query = """
            SELECT COUNT(DISTINCT 
                CASE 
                    WHEN sender_id = :user_id THEN receiver_id 
                    ELSE sender_id 
                END
            ) as count
            FROM private_messages 
            WHERE sender_id = :user_id OR receiver_id = :user_id
            """
            conversations_result = db.execute(conversations_query, {"user_id": user_id}).fetchone()
            conversations_count = conversations_result.count if conversations_result else 0
            
            return {
                "sent_count": sent_count,
                "received_count": received_count,
                "unread_count": unread_count,
                "conversations_count": conversations_count
            }
        except Exception as e:
            raise Exception(f"获取消息统计失败: {str(e)}")

class PrivateMessageData:
    """私信数据类"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.sender_id = kwargs.get('sender_id')
        self.receiver_id = kwargs.get('receiver_id')
        self.content = kwargs.get('content')
        self.message_type = kwargs.get('message_type', 'private')
        self.is_read = kwargs.get('is_read', False)
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at') 