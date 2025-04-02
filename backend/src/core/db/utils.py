from asgiref.sync import sync_to_async
from django.db.transaction import Atomic
from django.db.models import Model


class AsyncAtomicContextManager(Atomic):
    def __init__(self, using=None, savepoint=True, durable=False):
        super().__init__(using, savepoint, durable)

    async def __aenter__(self):
        await sync_to_async(super().__enter__)()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await sync_to_async(super().__exit__)(exc_type, exc_value, traceback)


class AsyncModelUtils:
    def __init__(self, model: type[Model], datasets: list[dict], unique_column: str):
        self.model = model
        self.datasets = datasets
        self.unique_column = unique_column

    async def update(self, dataset_ids):
        """Updates existing records in bulk"""
        if not self.datasets:
            return set()

        fields = list(self.datasets[0].keys())
        if self.unique_column in fields:
            fields.remove(self.unique_column)  # Exclude the unique identifier from updates

        # Fetch existing records from the database
        existing_objects = await sync_to_async(
            lambda: list(self.model.objects.filter(**{f"{self.unique_column}__in": dataset_ids}))
        )()

        # Update existing records
        updated_objects = []
        for obj in existing_objects:
            for field in fields:
                setattr(obj, field, next(
                    d[field] for d in self.datasets if d[self.unique_column] == getattr(obj, self.unique_column)))
            updated_objects.append(obj)

        # Ensure fields exist before calling bulk_update()
        if updated_objects and fields:
            await sync_to_async(self.model.objects.bulk_update)(updated_objects, fields, batch_size=100)

        existing_dataset_ids = {getattr(obj, self.unique_column) for obj in existing_objects}
        return existing_dataset_ids

    async def create(self, dataset_ids, existing_dataset_ids):
        """Creates new records if they do not exist in the database"""
        new_dataset_ids = set(dataset_ids) - existing_dataset_ids
        new_datasets = [d for d in self.datasets if d[self.unique_column] in new_dataset_ids]

        if new_datasets:
            try:
                # Use ignore_conflicts if supported by the database
                await sync_to_async(self.model.objects.bulk_create)(
                    [self.model(**d) for d in new_datasets], ignore_conflicts=True
                )
            except TypeError:
                # Fallback for databases that do not support ignore_conflicts
                await sync_to_async(self.model.objects.bulk_create)(
                    [self.model(**d) for d in new_datasets]
                )

    async def update_or_create(self) -> list["Model"]:
        """Performs bulk update for existing records and creates new ones in a single transaction"""
        dataset_ids = [d[self.unique_column] for d in self.datasets]

        async with AsyncAtomicContextManager():
            existing_dataset_ids = await self.update(dataset_ids)
            await self.create(dataset_ids, existing_dataset_ids)

        # Return all objects after update or creation
        objects = await sync_to_async(
            lambda: list(self.model.objects.filter(**{f"{self.unique_column}__in": dataset_ids})))()
        return objects
