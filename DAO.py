from models.SubscriptionModels import Hub, Subscription
from sqlalchemy import select
from database import async_session

async def delete_hub(id: int) -> bool:
    async with async_session() as session:
        await Hub.delete(id)
        statement = select(Subscription).where(Subscription.hub_id == id)
        result = await session.execute(statement)
        subscriptions = result.scalars().all()
        for subscription in subscriptions:
            await session.delete(subscription)
        await session.commit()
        return True
