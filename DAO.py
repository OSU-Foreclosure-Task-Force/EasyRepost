from models.SubscriptionModels import Hub, Subscription
from sqlalchemy.future import select
from database import AsyncSession


async def delete_hub(id: int) -> bool:
    async with AsyncSession() as session:
        await Hub.delete(id)
        statement = select(Subscription).where(Subscription.hub_id == id)
        result = await session.execute(statement)
        subscriptions = result.scalars().all()
        for subscription in subscriptions:
            await session.delete(subscription)
        await session.commit()
        return True
