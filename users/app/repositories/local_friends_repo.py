from uuid import UUID
from app.models.friends import Friends

# Локальное хранилище для друзей
friends: list[Friends] = []

class FriendsRepo:
    def get_friends(self) -> list[Friends]:
        return friends

    def get_friend_by_users(self, user1_id: UUID, user2_id: UUID) -> Friends:
        for friend in friends:
            if friend.user1_id == user1_id and friend.user2_id == user2_id:
                return friend
            if friend.user1_id == user2_id and friend.user2_id == user1_id:
                return friend
        raise KeyError(f"Friendship between user1_id={user1_id} and user2_id={user2_id} not found")

    def create_friend(self, friend: Friends) -> Friends:
        if any(
            (f.user1_id == friend.user1_id and f.user2_id == friend.user2_id) or
            (f.user1_id == friend.user2_id and f.user2_id == friend.user1_id)
            for f in friends
        ):
            raise KeyError("Friendship already exists")
        friends.append(friend)
        return friend

    def delete_friend(self, id: UUID) -> None:
        global friends
        friends = [f for f in friends if f.id != id]
