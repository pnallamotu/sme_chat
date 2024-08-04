# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""DataStore Module."""

import datetime
from typing import Any, Dict, List, Union

from google.cloud import datastore

from server.config.logging import logger


class DataStoreManager:
    """Saved element to Datastore."""
    def __init__(
        self,
        project_id: str,
        datastore_id: str,
    ):
        """Init saved recs.

        Args:
            project_id: Project ID of datastore DB.
            datastore_id: ID of datastore DB.
        """
        self.datastore_client = datastore.Client(
            project=project_id,
            database=datastore_id
        )

    def get_saved_elements(self, kind: str) -> List[Dict[str, Any]]:
        """Get saved entities from datastore.

        Args:
            Datastore kind to query (e.g: "Recipe").

        Returns:
            List of saved entity objects.
        """
        query = self.datastore_client.query(
            kind=kind
        )

        # Order by saved date.
        query.order = ["created"]

        results = list(query.fetch())

        # For FastAPI serialization.
        for result in results:
            result["created"] = result["created"].isoformat()

        return results

    def save_element(
        self,
        element_id: Union[str, int],
        kind: str,
        elem_key: str,
        element: Dict[str, Any],
    ) -> None:
        """Recommendation to save to datastore.

        Args:
            id: Unique id of element.
            kind: Datastore kind to save to.
            elem_key: Key of element to save as (e.g product, recipe, etc.).
            element: Element to upload to datastore.
        """
        try:
            # Create key for element to upload.
            key = self.datastore_client.key(kind, element_id)

            task = datastore.Entity(key)
            task.update(
                {
                    "created": datetime.datetime.now(tz=datetime.timezone.utc),
                    elem_key: element,
                }
            )
            self.datastore_client.put(task)
        except Exception as e:
            logger.error(f"Error saving recipe: {e}")
            raise e

    def delete_element(
        self,
        element_id: Union[str, int],
        kind: str,
    ):
        """Delete element from datastore."""
        try:
            key = self.datastore_client.key(kind, element_id)
            self.datastore_client.delete(key)
        except Exception as e:
            logger.error(f"Error deleting recipe: {e}")
